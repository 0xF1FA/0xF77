#!/usr/bin/env python3
"""Independent transition model, persistent-record controls, and restart checks.

The reference model lives only here. It is never imported by the running press.
"""
from __future__ import annotations

import argparse
import copy
from datetime import datetime, timezone
import hashlib
import itertools
import json
import os
from pathlib import Path
import random
import shlex
import subprocess
import tempfile

import cards
from engine import Press, compile_press

ROOT = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reference(cells, heads, genomes, rounds, *, frozen=False):
    """Ordinary integer model, independent of FORMAT offsets and card assembly."""
    cells, heads = copy.deepcopy(cells), copy.deepcopy(heads)
    trace = []
    offsets = dict(L=-1, S=0, R=1, U=2)
    for _ in range(rounds):
        for i, h in enumerate(heads):
            pos = h["pos"]
            c = cells[pos - 1]
            before = c["color"]
            g = genomes[h["genome"]]
            successors = g.get("next", [(j + 1) % len(g["turns"])
                                         for j in range(len(g["turns"]))])
            after = successors[before]
            turn = g["turns"][before]
            stamp = g.get("stamps", "." * len(g["turns"]))[before]
            if not frozen:
                c["color"] = after
                if stamp == ".":
                    c["imprint"] = h["home"]
                else:
                    c["links"]["NESW".index(stamp)] = h["home"]
            h["heading"] = (h["heading"] + offsets[turn]) % 4
            h["pos"] = c["links"][h["heading"]]
            trace.append([i, pos, h["pos"], before, after, h["heading"],
                          *c["links"], "LSRU".index(turn), ".NESW".index(stamp)])
    return cells, heads, trace


def snapshot_model(directory):
    return ([cards.decode_cell(r) for r in cards.records(directory / "world.spool")],
            [cards.decode_head(r) for r in cards.records(directory / "heads.spool")])


def compare(executable, directory, rounds, spec, *, raw_path=None):
    cells, heads = snapshot_model(directory)
    ec, eh, et = reference(cells, heads, spec["genomes"], rounds)
    result = Press(directory, executable).step(rounds, raw_path=raw_path)
    assert result["trace"] == et, "Native trajectory differs from independent integer model"
    nc, nh = snapshot_model(directory)
    assert nc == ec, "Persistent cell state/links/imprint differ"
    assert nh == eh, "Persistent head state differs"
    expected_world = "".join(cards.cell_record(**c) for c in ec).encode("ascii")
    expected_heads = "".join(cards.head_record(**h) for h in eh).encode("ascii")
    assert (directory / "world.spool").read_bytes() == expected_world
    assert (directory / "heads.spool").read_bytes() == expected_heads
    return dict(transitions=len(et), world_sha256=digest(directory / "world.spool"),
                heads_sha256=digest(directory / "heads.spool"),
                changed_ports=sum(a != b for c, old in zip(ec, cells)
                                  for a, b in zip(c["links"], old["links"])))


def random_spec(rng, case):
    w, h = rng.randrange(2, 11), rng.randrange(2, 9)
    count = w * h
    colors = [2, 3, 4, 8][case % 4]
    genomes = [dict(name=f"g{i}", turns="".join(rng.choice("LSRU") for _ in range(colors)),
                    stamps="".join(rng.choice(".NESW") for _ in range(colors)),
                    next=[rng.randrange(colors) for _ in range(colors)])
               for i in range(1 + case % 8)]
    heads = [dict(pos=rng.randrange(1, count + 1), heading=rng.randrange(4),
                  genome=rng.randrange(len(genomes)), home=rng.randrange(1, count + 1))
             for _ in range(1 + case % 6)]
    return dict(title="verification", subtitle="independent graph corpus", width=w, height=h,
                colors=colors, rounds=120, agents=len(heads), genomes=genomes, heads=heads,
                initial=[rng.randrange(colors) for _ in range(count)],
                links=[[rng.randrange(1, count + 1) for _ in range(4)] for _ in range(count)])


def suite(output, fc):
    evidence = dict(timestamp=datetime.now(timezone.utc).isoformat(),
                    model="independent integer graph-rewriting turmite in test_press.py",
                    profiles=[], failures=[])
    total = 0
    with tempfile.TemporaryDirectory(prefix="carbon-verify-") as temp:
        temp = Path(temp)
        for opt in ("-O0", "-O2", "-O3"):
            build = compile_press(temp / opt, optimization=opt, fc=fc)
            executable = Path(build["executable"])
            profile = dict(optimization=opt, build=build, cases=[])
            try:
                # Every two-color turn rule, every initial heading and color;
                # cells form a fixed small torus. This checks relative turning
                # independently of the native compass offsets.
                for turns in itertools.product("LSRU", repeat=2):
                    for heading in range(4):
                        for color in range(2):
                            spec = dict(title="turn corpus", subtitle="", width=4, height=3,
                                        colors=2, genomes=[dict(name="g", turns="".join(turns), stamps="..")],
                                        heads=[dict(pos=6, home=6, heading=heading, genome=0)],
                                        initial=[color] * 12)
                            directory = temp / "case"
                            seeded = cards.seed(directory, model=spec)
                            result = compare(executable, directory, 48, seeded)
                            profile["cases"].append(dict(kind="turns", turns="".join(turns),
                                                          heading=heading, color=color, **result))
                rng = random.Random(0xF77A)
                for i in range(48):
                    spec = random_spec(rng, i)
                    directory = temp / "case"
                    seeded = cards.seed(directory, model=spec)
                    result = compare(executable, directory, 120, seeded)
                    profile["cases"].append(dict(kind="random graph", seed=0xF77A, case=i, **result))
                for name, preset in cards.PRESETS.items():
                    directory = temp / name
                    spec = cards.seed(directory, name)
                    result = compare(executable, directory, preset["rounds"], spec,
                                     raw_path=(output.parent / "witness.txt" if opt == "-O2" and
                                               name == "afterimage" else None))
                    profile["cases"].append(dict(kind="full specimen", name=name, **result))

                # New subprocesses run each segment. Compare all three persisted
                # files after 1200 rounds vs 317+883, not just visible marks.
                one, split = temp / "one", temp / "split"
                cards.seed(one); cards.seed(split)
                Press(one, executable).step(1200)
                Press(split, executable).step(317)
                checkpoint = temp / "checkpoint.zip"
                Press(split, executable).checkpoint(checkpoint)
                import zipfile
                restored = temp / "restored"
                with zipfile.ZipFile(checkpoint) as archive:
                    archive.extractall(restored)
                Press(restored, executable).step(883)
                for name in ("world.spool", "heads.spool", "world.json"):
                    assert (one / name).read_bytes() == (restored / name).read_bytes(), name
                profile["restart"] = dict(passed=True, split=[317, 883], rounds=1200,
                                           hashes={n: digest(one / n) for n in
                                                   ("world.spool", "heads.spool", "world.json")})

                # Native memory ablation: replace only the full-record flush
                # with a Fortran comment. Frozen external cells must match the
                # frozen model and must diverge from the original trajectory.
                mutant = temp / "frozen.f"
                source = (ROOT / "press.f").read_text()
                old = "          WRITE(21,'(A80)',REC=POS) PATCH"
                assert source.count(old) == 1
                mutant.write_text(source.replace(old, "C" + old[1:]))
                frozen = temp / "frozen"
                compile_result = subprocess.run([*shlex.split(fc or os.environ.get("FC", "gfortran")),
                                                 "-std=f95", opt, str(mutant), "-o", str(frozen)],
                                                capture_output=True, text=True, timeout=60)
                assert compile_result.returncode == 0, compile_result.stderr
                directory = temp / "ablation"
                spec = cards.seed(directory)
                cells, heads = snapshot_model(directory)
                fcells, fheads, ftrace = reference(cells, heads, spec["genomes"], 80, frozen=True)
                _, _, normal_trace = reference(cells, heads, spec["genomes"], 80)
                actual = Press(directory, frozen).step(80)["trace"]
                assert actual == ftrace and actual != normal_trace
                assert snapshot_model(directory) == (fcells, fheads)
                profile["memory_ablation"] = dict(passed=True, transitions=len(actual),
                                                  differs_from_unablated=True)

                # A requested two-ended splice is persisted, followed by real
                # native traversal. Painting and genome editing are explicit
                # interventions, then the same fixed press continues.
                directory = temp / "interventions"
                spec = cards.seed(directory, "highway")
                press = Press(directory, executable)
                first = spec["heads"][0]["pos"]
                target = 2
                press.fold(first, target)
                press.paint([first, target], 0)
                press.edit_genome(0, "RS", "..")
                result = compare(executable, directory, 64, press.spec())
                assert cards.decode_head(cards.records(directory / "heads.spool")[0])["pos"] != first
                profile["interventions"] = dict(passed=True, **result)

                # Native error rollback: damaged code in a reachable tile
                # must not partially advance the persistent world or heads.
                directory = temp / "error"
                spec = cards.seed(directory, "highway")
                p = spec["heads"][0]["pos"]
                with (directory / "world.spool").open("r+b") as spool:
                    spool.seek((p - 1) * 80); spool.write(b" " * 32)
                before = {name: (directory / name).read_bytes() for name in
                          ("world.spool", "heads.spool", "world.json")}
                try:
                    Press(directory, executable).step(4)
                    raise AssertionError("Damaged executable tile was accepted")
                except RuntimeError:
                    pass
                assert all((directory / name).read_bytes() == data for name, data in before.items())
                profile["native_error_rollback"] = dict(passed=True)
                profile["passed"] = True
            except Exception as exc:
                profile["passed"] = False
                profile["failure"] = repr(exc)
                evidence["failures"].append(f"{opt}: {exc!r}")
            profile["transitions_compared"] = sum(c["transitions"] for c in profile["cases"])
            total += profile["transitions_compared"]
            evidence["profiles"].append(profile)
    # Keep a small inspectable native witness instead of all repeated formats.
    witness = output.parent / "witness.txt"
    if witness.exists():
        witness.write_text("\n".join(witness.read_text().splitlines()[:128]) + "\n")
    evidence["total_transitions_compared"] = total
    evidence["passed"] = not evidence["failures"]
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(evidence, indent=2) + "\n")
    print(json.dumps(dict(passed=evidence["passed"], transitions_compared=total,
                          failures=evidence["failures"], evidence=str(output))))
    return evidence["passed"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "evidence" / "native.json")
    parser.add_argument("--fc", default=None)
    args = parser.parse_args()
    raise SystemExit(0 if suite(args.output, args.fc) else 1)
