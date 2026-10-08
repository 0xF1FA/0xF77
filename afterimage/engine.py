"""Compile and transport CARBON's native records. There is no Python step model."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import tempfile
import threading

import cards

ROOT = Path(__file__).resolve().parent


def compile_press(build: Path, *, optimization: str = "-O2", fc: str | None = None) -> dict:
    build.mkdir(parents=True, exist_ok=True)
    compiler = shlex.split(fc or os.environ.get("FC", "gfortran"))
    command = [*compiler, "-std=f95", optimization, "-Wall", "-Wextra",
               str(ROOT / "press.f"), "-o", str(build / "press")]
    try:
        proc = subprocess.run(command, text=True, capture_output=True, timeout=60)
    except FileNotFoundError as exc:
        raise RuntimeError("Install GNU Fortran, or set FC to a compiler command.") from exc
    if proc.returncode:
        raise RuntimeError(proc.stderr or "Fortran compilation failed")
    version = subprocess.run([*compiler, "--version"], capture_output=True,
                             text=True, timeout=10)
    linkage = subprocess.run(["ldd", str(build / "press")], capture_output=True,
                             text=True, timeout=10)
    return dict(command=command, compiler=version.stdout, warnings=proc.stderr,
                linkage=linkage.stdout,
                source_sha256=hashlib.sha256((ROOT / "press.f").read_bytes()).hexdigest(),
                executable=str(build / "press"))


def decode_trace(raw: str) -> list[list[int]]:
    headings = {cards.heading_card(i).strip(): i for i in range(4)}
    colors = {cards.color_card(i).strip(): i for i in range(cards.MAX_COLORS)}
    turns = {cards.turn_card(t).strip(): i for i, t in enumerate(cards.TURNS)}
    stamps = {cards.stamp_card(p).strip(): i for i, p in enumerate(".NESW")}
    moves = {cards.move_card(i).strip(): i for i in range(4)}
    result = []
    for line in raw.splitlines():
        fields = line.split()
        if len(fields) != 15:
            raise RuntimeError("Malformed native trace")
        tick, head, pos, dest = map(int, fields[:4])
        before, after = int(fields[4]), int(fields[5])
        heading = headings[fields[6]]
        if colors[fields[7]] != after or moves[fields[10]] != heading:
            raise RuntimeError("Native code and trace annotation disagree")
        # Round and head are sequential transport metadata. Formats are decoded
        # for viewing; this function never chooses any successor or evaluates it.
        result.append([head - 1, pos, dest, before, after, heading,
                       *map(int, fields[11:15]), turns[fields[8]], stamps[fields[9]]])
    return result


def instructions() -> dict:
    return dict(colors=[cards.color_card(i).strip() for i in range(8)],
                headings=[cards.heading_card(i).strip() for i in range(4)],
                turns=[cards.turn_card(t).strip() for t in cards.TURNS],
                stamps=[cards.stamp_card(p).strip() for p in ".NESW"],
                moves=[cards.move_card(i).strip() for i in range(4)])


class Press:
    def __init__(self, directory: Path, executable: Path):
        self.directory = directory.resolve()
        self.executable = executable.resolve()
        self.lock = threading.RLock()

    def spec(self) -> dict:
        return json.loads((self.directory / "world.json").read_text())

    def save_spec(self, spec: dict):
        (self.directory / "world.json").write_text(json.dumps(spec, indent=2) + "\n")

    def snapshot(self) -> dict:
        with self.lock:
            spec = self.spec()
            cells = [cards.decode_cell(r) for r in cards.records(self.directory / "world.spool")]
            heads = [cards.decode_head(r) for r in cards.records(self.directory / "heads.spool")]
            ordinary = cards.grid_links(spec["width"], spec["height"])
            edges = [[i + 1, p, dest] for i, c in enumerate(cells)
                     for p, dest in enumerate(c["links"]) if dest != ordinary[i][p]]
            return dict(spec=spec, initial="".join(str(c["color"]) for c in cells),
                        heads=heads, edges=edges,
                        imprints=[[i + 1, c["imprint"]] for i, c in enumerate(cells)
                                  if c["imprint"]],
                        trace=[], instructions=instructions(),
                        core=(ROOT / "press.f").read_text())

    def step(self, rounds: int, *, raw_path: Path | None = None) -> dict:
        if not isinstance(rounds, int) or not 1 <= rounds <= 20000:
            raise ValueError("Batch must contain 1..20000 rounds")
        with self.lock:
            spec = self.spec()
            with tempfile.TemporaryDirectory(prefix="carbon-press-") as temp:
                temp = Path(temp)
                for name in ("world.spool", "heads.spool"):
                    shutil.copyfile(self.directory / name, temp / name)
                world, heads = temp / "world.spool", temp / "heads.spool"
                data = "\n".join([str(world), str(heads),
                    f"{rounds} {len(spec['heads'])} {spec['round']}",
                    cards.library(spec["genomes"], spec["colors"]), cards.compass()]) + "\n"
                proc = subprocess.run([str(self.executable)], input=data,
                                      text=True, capture_output=True, timeout=60)
                if proc.returncode:
                    raise RuntimeError("Native press stopped; the previous world is intact.\n" +
                                       proc.stderr[-2000:])
                trace = decode_trace(proc.stdout)
                if len(trace) != rounds * len(spec["heads"]):
                    raise RuntimeError("Native trace length disagrees with the clock")
                if world.stat().st_size != (self.directory / "world.spool").stat().st_size:
                    raise RuntimeError("Native world record extent changed")
                if heads.stat().st_size != (self.directory / "heads.spool").stat().st_size:
                    raise RuntimeError("Native head record extent changed")
                # Failed native batches never replace the prior state. This is
                # a process-level transaction, not a power-loss journal.
                for name in ("world.spool", "heads.spool"):
                    os.replace(temp / name, self.directory / name)
                spec["round"] += rounds
                self.save_spec(spec)
                if raw_path:
                    raw_path.parent.mkdir(parents=True, exist_ok=True)
                    raw_path.write_text(proc.stdout)
                return dict(trace=trace, round=spec["round"])

    def paint(self, positions: list[int], color: int):
        with self.lock:
            spec = self.spec()
            if not isinstance(color, int) or not 0 <= color < spec["colors"]:
                raise ValueError("Color outside this world's alphabet")
            total = spec["width"] * spec["height"]
            if len(positions) > 4096 or any(not isinstance(p, int) or not 1 <= p <= total
                                         for p in positions):
                raise ValueError("Invalid paint addresses")
            with (self.directory / "world.spool").open("r+b") as spool:
                for pos in positions:
                    spool.seek((pos - 1) * 80)
                    spool.write((cards.color_card(color) + str(color)).encode("ascii"))

    def fold(self, first: int, second: int):
        with self.lock:
            spec = self.spec()
            total = spec["width"] * spec["height"]
            if not all(isinstance(p, int) and 1 <= p <= total for p in (first, second)):
                raise ValueError("Invalid portal addresses")
            # Explicit user intervention: splice first's east port and second's
            # west port. Subsequent traversal and further rewriting are native.
            with (self.directory / "world.spool").open("r+b") as spool:
                for pos, port, dest in ((first, 1, second), (second, 3, first)):
                    spool.seek((pos - 1) * 80 + 40 + port * 8)
                    spool.write(f"{dest:8d}".encode("ascii"))

    def edit_genome(self, index: int, turns: str, stamps: str):
        with self.lock:
            spec = self.spec()
            if not isinstance(index, int) or not 0 <= index < len(spec["genomes"]):
                raise ValueError("Invalid genome")
            spec["genomes"][index]["turns"] = turns
            spec["genomes"][index]["stamps"] = stamps
            cards.library(spec["genomes"], spec["colors"])
            self.save_spec(spec)

    def checkpoint(self, path: Path):
        import zipfile
        with self.lock, zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
            for name in ("world.spool", "heads.spool", "world.json"):
                archive.write(self.directory / name, name)


def export_replay(preset: str, executable: Path, directory: Path) -> dict:
    cards.seed(directory, preset)
    press = Press(directory, executable)
    payload = press.snapshot()
    output = press.step(cards.PRESETS[preset]["rounds"])
    payload["trace"] = output["trace"]
    payload["final_sha256"] = {name: hashlib.sha256((directory / name).read_bytes()).hexdigest()
                               for name in ("world.spool", "heads.spool")}
    return payload
