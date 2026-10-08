# CARBON / AFTERIMAGE

An ecology of executable paper. Six creatures walk a shared world, rewrite its
ground instructions, and sometimes punch passages back to their homes. What
looks like a cellular drawing is a persistent graph of native Fortran records.

The 50-line press chooses rules, rotates creatures, rewrites cards, and follows
graph ports using the compiler's FORMAT machinery. Its transition path contains
no state arithmetic, conditional dispatch, or application-indexed lookup table.

Run the live instrument with **Python 3.10+ and GNU Fortran**:

```sh
cd afterimage
python3 afterimage.py --serve --open
```

The viewer opens at `http://127.0.0.1:1977`. Use `--port N` if that port is busy.
Set `FC` to a compiler command and arguments when needed. The ordinary press has
no Python packages, Node packages, remote assets, or browser transition engine.

If you downloaded a ZIP instead of cloning with Git, update it by downloading
the latest ZIP and copying only the program files over the extracted
`afterimage/` directory. This preserves your persistent `world/` directory:

```sh
cd /path/to/0xF77-main/afterimage
mkdir -p /tmp/carbon-update
curl -L https://github.com/0xF1FA/0xF77/archive/refs/heads/main.zip \
  -o /tmp/carbon-update/0xF77-main.zip
unzip -q -o /tmp/carbon-update/0xF77-main.zip -d /tmp/carbon-update
cp -a /tmp/carbon-update/0xF77-main/afterimage/. .
```

The ZIP contains no `.git` directory, so `git pull` is only available when the
repository was installed with `git clone`. Do not delete `world/` when updating
a ZIP installation; it contains the current world state.

The downloadable `CARBON-AFTERIMAGE.html` opens directly in a browser without a
compiler. It contains three measured native runs: 59,200 actual transitions,
not a JavaScript simulation. Rebuild it from the source with:

```sh
python3 afterimage.py --export CARBON-AFTERIMAGE.html
```

## Touch the world

- **Inspect:** click a tile to see its executable card and stored neighbors.
  Follow a creature to watch the last rule, stamp, and movement format it used.
- **Paint:** choose a state, then drag to print those cards into the ground.
- **Splice:** choose two tiles. The first tile's east port points to the second;
  the second tile's west port points back. Subsequent moves follow those stored
  record addresses.
- **Edit a genome:** each character describes one ground state. Turns are
  `L` left, `S` straight, `R` right, and `U` reverse. Stamps are `.` ordinary
  imprint, or `N/E/S/W` to replace that port with the visiting creature's home
  address. Native FORMAT performs the replacement on the next visit.
- **Save this world:** download the current world, creatures, rules, and clock
  as a checkpoint. Extract it into a directory and resume it:

```sh
python3 afterimage.py --world /path/to/extracted-world --resume --serve --open
```

For a command-line run and the complete raw native trace:

```sh
python3 afterimage.py --preset afterimage --rounds 1200 --raw witness.txt
python3 afterimage.py --world world --resume --rounds 1200
```

Without `--resume`, the command seeds a new world in the selected directory.
Specimen tabs in the live instrument also seed a fresh world. Save an existing
world before replacing it. Switching tabs in the offline instrument selects
one of its immutable recorded runs.

## Three specimens

| Sheet | Creatures | Rules | Native transitions in the replay |
| --- | ---: | --- | ---: |
| Afterimage | 6 | A shared four-state ground; weaver, east-burrower, north-recoil genomes | 25,200 |
| The folded sheet | 4 | Opposite vertical coordinates meet at the east/west seam; weavers and burrowers | 20,000 |
| One creature | 1 | Two-state `RL` turn cards, ordinary imprints | 14,000 |

The drawing shows geometric coordinates, while motion follows stored graph
links. A creature can leave that geometric neighborhood through a folded seam
or a passage made by an earlier visit. Ordinary imprints retain a home address
in the spare tail of a cell. Burrow stamps put that same value in a graph port.
Creatures share the same writable ground, so their visits affect one another.

## The native mechanism

The rule library and compass are assembled before execution. A tile contains a
real input FORMAT such as `(T0130:A32:A32:A64:A1)`: select a successor card,
a turn card, an output stamp, and a visible state byte from the current genome.

```fortran
          READ(RULES,CODE) NEXT,TURN,STAMP,MARK
          WRITE(PATCH,STAMP) CELL,NEXT,MARK,HOME
          WRITE(21,'(A80)',REC=POS) PATCH
          READ(COMPASS,HEADING) TURNS,MOVE
          READ(TURNS,TURN) HEADING
          READ(COMPASS,HEADING) TURNS,MOVE
          READ(21,'(A80)',REC=POS) CELL
          READ(CELL,MOVE) DEST
```

`NEXT` becomes the ground's next executable selector. `HEADING` is itself an
executable FORMAT, rather than an integer rotated by the host. `MOVE` selects a
stored graph port and converts its decimal address to the integer supplied to
the next `REC=` access. A normal stamp is
`(A80:T1:A32:T33:A1:T73:I8)`; an east burrow changes `T73` to `T49`.
Both are executed by native formatted output.

Records are 80 ASCII bytes with no newline or native unformatted-record wrapper:

| Cell columns, 1-based | Meaning |
| --- | --- |
| 1–32 | Executable ground selector |
| 33 | Visible state byte, checked against the selector |
| 34–40 | Padding |
| 41–48, 49–56, 57–64, 65–72 | N/E/S/W decimal record addresses |
| 73–80 | Home imprint |

A creature record has address `I8`, heading FORMAT `A32`, genome FORMAT `A32`,
and home address `I8`. The compass contains all relative-turn outcomes as
literal successor FORMAT cards. Python assembles those cards; it does not choose
turns or destinations while the machine runs.

## Responsibility and limits

| Layer | Work it actually does |
| --- | --- |
| Native FORMAT | Ground-rule selection; successor selector copying; relative-turn selection; record copying/overwriting; graph-port selection; decimal address conversion |
| Fixed Fortran pump | Clock and ordered creature iteration; direct-record access through `REC=`; buffer transport; trace output |
| Python | Offline assembly, compilation, explicit user interventions, failed-batch rollback, checkpoint packaging, local HTTP transport |
| Browser | Drawing and inspecting observed native events; replay controls; submitting explicit live interventions |

This is CARBON II with persistent writable spatial memory and autonomous link
rewriting. It is distinct from the original numeric-plate CARBON mechanism.
The node set is fixed per world; allocation, `REC=`, creature scheduling, and the
clock remain host services. The assembled library supports 2–8 symbols and
1–8 genomes. This work does not demonstrate unbounded storage, universality,
independent-compiler portability, or a power-loss journal. Failed native
batches preserve the previous files; successful replacement of all checkpoint
files is a process-level transaction, not an atomic filesystem-wide commit.

## Evidence

```sh
python3 test_press.py --output evidence/current.json
```

Two tested bindings: GNU Fortran 13.3 with static libgfortran 13.3, and the same
compiler with explicitly bound shared libgfortran 14.2. Each ran `-O0`, `-O2`
and `-O3` under `-std=f95`. Each profile checks 128 exhaustive two-color
turn/heading/initial-color cases, 48 seeded arbitrary graph/genome cases, and
all three full specimens against an independent integer model. **513,024
transitions matched**, including every successor, link rewrite and trace field;
final world and creature files also matched exactly.

Controls check a 317+883-round restart against a 1,200-round uninterrupted run,
checkpoint extraction into a different directory, native-write ablation,
painting/splicing/genome intervention, and rollback on damaged executable code.
The reference evaluator exists only in `test_press.py`.

The optional Playwright check uses a real browser, exercises replay and live
controls, checks a 390px mobile layout, and reconstructs every final spool byte
from all three replays to match native SHA-256 hashes:

```sh
node test_browser.cjs /absolute/path/CARBON-AFTERIMAGE.html
```

Install Playwright and its Chromium for that optional check, or set
`CARBON_PLAYWRIGHT` to its module path and `CARBON_CHROMIUM` to an available
browser binary. Neither is needed to run AFTERIMAGE normally.

### A retained medium failure

The initial implementation stamped directly into a direct-access external
record. Under both tested GNU runtime bindings, the sequence
`WRITE(unit,'(A80:T1:A32:T33:A1:T49:I8)',REC=1)` damaged the next record:
its first 24 bytes became spaces. This is an observed implementation behavior,
not a claimed Fortran rule. `direct_seam.f` is the minimal reproducer;
`evidence/direct-seam.json` retains commands, raw output and runtime hashes.

The press now executes the same native stamp into a separate internal character
record and flushes the complete 80-byte result with a simple `A80` external
write. The control preserves the next record; the complete independent-model
corpus verifies every persisted byte. The failed route remains inspectable.
