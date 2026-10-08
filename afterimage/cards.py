"""Offline assembly of executable cards. No transition evaluator is used live."""
from __future__ import annotations

import json
import math
from pathlib import Path

CELL_BYTES = HEAD_BYTES = 80
RULE_BYTES = 129
GENOME_BYTES = 1152
MAX_GENOMES = MAX_COLORS = 8
LIBRARY_BYTES = MAX_GENOMES * GENOME_BYTES
PORTS = "NESW"
TURNS = "LSRU"


def padded(fmt: str, width: int = 32) -> str:
    if len(fmt) > width or "," in fmt:
        raise ValueError("Card exceeds its storage width or contains a comma")
    return fmt.ljust(width)


def color_card(color: int) -> str:
    return padded(f"(T{1 + color * RULE_BYTES:04d}:A32:A32:A64:A1)")


def heading_card(heading: int) -> str:
    return padded(f"(T{1 + heading * 160:04d}:A128:A32)")


def turn_card(turn: str) -> str:
    return padded(f"(T{1 + TURNS.index(turn) * 32:04d}:A32)")


def move_card(heading: int) -> str:
    return padded(f"(T{41 + heading * 8:04d}:I8)")


def genome_card(genome: int) -> str:
    return padded(f"(T{1 + genome * GENOME_BYTES:04d}:A1152)")


def stamp_card(port: str = ".") -> str:
    # The ordinary stamp writes a creator's home in the spare tail. A burrow
    # stamp writes it into a graph port instead. The runtime does the overwrite.
    column = 73 if port == "." else 41 + PORTS.index(port) * 8
    return padded(f"(A80:T1:A32:T33:A1:T{column}:I8)", 64)


def library(genomes: list[dict], colors: int) -> str:
    if not 2 <= colors <= MAX_COLORS or not 1 <= len(genomes) <= MAX_GENOMES:
        raise ValueError("Use 2..8 colors and 1..8 genomes")
    rows = []
    for genome in genomes:
        turns, stamps = genome["turns"], genome.get("stamps", "." * colors)
        if len(turns) != colors or len(stamps) != colors:
            raise ValueError("Every genome must describe every color")
        if any(t not in TURNS for t in turns) or any(p not in ".NESW" for p in stamps):
            raise ValueError("Turns are L/S/R/U; stamps are . or N/E/S/W")
        successors = genome.get("next", [(i + 1) % colors for i in range(colors)])
        if len(successors) != colors or any(not 0 <= s < colors for s in successors):
            raise ValueError("Invalid successor color")
        row = "".join(color_card(successors[c]) + turn_card(turns[c]) +
                      stamp_card(stamps[c]) + str(successors[c])
                      for c in range(colors))
        rows.append(row.ljust(GENOME_BYTES))
    return "".join(rows).ljust(LIBRARY_BYTES)


def compass() -> str:
    offsets = [-1, 0, 1, 2]
    return "".join("".join(heading_card((h + d) % 4) for d in offsets) +
                   move_card(h) for h in range(4))


def cell_record(color: int, links: list[int], imprint: int = 0) -> str:
    if len(links) != 4 or any(not 1 <= v <= 99999999 for v in links):
        raise ValueError("Four valid record addresses required")
    return color_card(color) + str(color) + " " * 7 + \
        "".join(f"{v:8d}" for v in links) + f"{imprint:8d}"


def head_record(pos: int, heading: int, genome: int, home: int) -> str:
    return f"{pos:8d}" + heading_card(heading) + genome_card(genome) + f"{home:8d}"


def decode_cell(record: str) -> dict:
    color = int(record[32])
    if record[:32] != color_card(color):
        raise ValueError("Glyph and executable color card disagree")
    return dict(color=color, links=[int(record[40 + i * 8:48 + i * 8])
                                   for i in range(4)], imprint=int(record[72:80]))


def decode_head(record: str) -> dict:
    hmap = {heading_card(i): i for i in range(4)}
    gmap = {genome_card(i): i for i in range(MAX_GENOMES)}
    return dict(pos=int(record[:8]), heading=hmap[record[8:40]],
                genome=gmap[record[40:72]], home=int(record[72:80]))


def records(path: Path) -> list[str]:
    data = path.read_bytes()
    if len(data) % CELL_BYTES:
        raise ValueError("Damaged spool: record width is not 80 bytes")
    return [data[i:i + CELL_BYTES].decode("ascii")
            for i in range(0, len(data), CELL_BYTES)]


def grid_links(width: int, height: int, folded: bool = False) -> list[list[int]]:
    def address(x, y):
        return (y % height) * width + (x % width) + 1
    result = []
    for y in range(height):
        for x in range(width):
            e_y = height - 1 - y if folded and x == width - 1 else y
            w_y = height - 1 - y if folded and x == 0 else y
            result.append([address(x, y - 1), address(x + 1, e_y),
                           address(x, y + 1), address(x - 1, w_y)])
    return result


PRESETS = {
    "afterimage": dict(title="Afterimage", subtitle="Six creatures. One shared memory.",
                      width=96, height=72, colors=4, rounds=4200,
                      genomes=[dict(name="WEAVER", turns="RLLR", stamps="...."),
                               dict(name="BURROWER", turns="LRRL", stamps="..E."),
                               dict(name="RECOIL", turns="RSUL", stamps="...N")],
                      agents=6, folded=False),
    "fold": dict(title="The folded sheet", subtitle="The edge returns you upside down.",
                 width=96, height=72, colors=4, rounds=5000,
                 genomes=[dict(name="WEAVER", turns="RLLR", stamps="...."),
                          dict(name="BURROWER", turns="LRRL", stamps="..E.")],
                 agents=4, folded=True),
    "highway": dict(title="One creature", subtitle="Two cards. A very long afterimage.",
                    width=112, height=96, colors=2, rounds=14000,
                    genomes=[dict(name="CLASSIC", turns="RL", stamps="..")],
                    agents=1, folded=False),
}


def seed(directory: Path, preset: str = "afterimage", *, model: dict | None = None) -> dict:
    directory.mkdir(parents=True, exist_ok=True)
    spec = json.loads(json.dumps(model or PRESETS[preset]))
    width, height = spec["width"], spec["height"]
    links = spec.get("links") or grid_links(width, height, spec.get("folded", False))
    colors = spec.get("initial", [0] * len(links))
    if len(links) != width * height or len(colors) != len(links):
        raise ValueError("Initial world dimensions disagree")
    if any(not 0 <= c < spec["colors"] for c in colors):
        raise ValueError("Initial color outside genome alphabet")
    heads = spec.get("heads")
    if heads is None:
        heads = []
        for i in range(spec["agents"]):
            if spec["agents"] == 1:
                x, y = width // 2, height // 2
            else:
                angle = 2 * math.pi * i / spec["agents"]
                x = width // 2 + round(math.cos(angle) * width * .16)
                y = height // 2 + round(math.sin(angle) * height * .16)
            pos = y * width + x + 1
            heads.append(dict(pos=pos, heading=i % 4,
                              genome=i % len(spec["genomes"]), home=pos))
    spec["heads"] = heads
    spec["round"] = 0
    spec["preset"] = preset
    spec.pop("links", None)
    spec.pop("initial", None)
    library(spec["genomes"], spec["colors"])
    (directory / "world.spool").write_bytes("".join(
        cell_record(c, ls) for c, ls in zip(colors, links)).encode("ascii"))
    (directory / "heads.spool").write_bytes("".join(head_record(**head)
                                                   for head in heads).encode("ascii"))
    (directory / "world.json").write_text(json.dumps(spec, indent=2) + "\n")
    return spec
