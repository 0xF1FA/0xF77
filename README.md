# CARBON II: mutable FORMAT as a machine

The runnable next experiment is **[CARBON / AFTERIMAGE](afterimage/README.md)**:
a persistent world of executable ground cards. Creatures rewrite those cards
and can stamp new graph links with native FORMAT output. It includes a live
instrument, checkpoint restore and a portable viewer of measured native runs.

```sh
cd afterimage
python3 afterimage.py --serve --open
```

The new result is a finite-state transducer whose transition lookup is performed
by two FORMAT-controlled reads. The Fortran harness has no state arithmetic,
state-indexed array lookup, or conditional dispatch. The transition table is
assembled as a record before execution.

```fortran
        READ(TABLE,STATE) ROW
        READ(ROW,SYMBOL) STATE
```

STATE and SYMBOL contain executable FORMAT descriptions. ROW contains the
possible successor descriptions for the current state. The second read selects
the successor, which controls the first read on the next clock tick.

The host supplies a finite clock and transports buffers. It does not disappear.
This is a result for FORMAT plus records plus a fixed I/O pump, not autonomous
FORMAT execution or a proof of Turing completeness.

Run with Python 3 and GNU Fortran:

```sh
python3 run.py
python3 demo.py
python3 demo.py --external
python3 demo.py --example parity --word 10110100111
```

Set `FC` to a compiler command and arguments when needed. The original experiment
used GNU Fortran 13.3.0 and its static libgfortran 13.3.0 runtime on x86-64 Ubuntu.
Exact commands, outputs, expected traces, source hashes and runtime linkage are
in `evidence/results.json`. The installed shared runtime is a different version
and was not the runtime used for these results.

The test corpus contains all 16 two-state/two-symbol transition tables and all
31 words of length zero through four, plus 32 seeded larger-table traces.
All 528 traces passed at each of `-O0`, `-O2` and `-O3`: 1,584 traces total.
Five representative automata also run through external records at each level.

Keep the medium seam visible: under `-std=legacy`, internal A reads stop at a
comma, even for standard CHARACTER targets; external A reads preserve it.
Under `-std=gnu` and `-std=f95`, both preserve it in the measured specimen.
The comma-containing internal automaton fails in legacy mode. The separately
tested colon-separated vocabulary works: the colon descriptor does nothing
while an I/O item remains. This is an alternate valid representation, not an
erasure of the failed specimen. The matrix retains both results.

The new probes also show native list-exhaustion selection, bounded reversion,
indirect record addressing, syntax construction, bounded storage shifts and two
individually idempotent transition systems whose alternation cycles.

`instruction_set.csv` records operational effects, descriptor dating, media
behavior and evidence. `assessment.md` states the responsibility split and
limits. `evidence/source_audit.json` pins the runtime source inspected.

At the original CARBON II measurement, the earlier four-state loop and checkpoint
result were inherited from the task brief; their sources were not retrievable.
They have now been recovered unchanged in `baseline/carbon/` and retested with
both static GNU 13.3 and shared libgfortran 14.2. All 37 checks passed under each
binding, and all four historical payloads match byte for byte. The original
CARBON II corpus was independently rerun: all 1,584 traces passed again.
See `RECONCILIATION.md` and the separately dated files in `evidence/`.

Run the original numeric-plate machine and preserve its historical evidence:

```sh
cd baseline/carbon
sh run.sh
cd ../..
python3 tools/reverify_baseline.py --output evidence/baseline-current.json
```

The original 31-page research/design dossier, updated with the forward work,
is in `research/report/report.pdf`. Its ReportLab authoring sources are beside
it. The report contains 28 mechanisms, ten distinct concepts, the scored
shortlist, the selected architecture, eight outsider predictions and the new
reproduction findings. No novelty claim is made for formatting computation,
self-copying, or runtime FORMAT descriptions themselves.

The current limits include fixed-capacity records, host-supplied repeated I/O,
and no demonstrated growing read/write tape, autonomous general predicate
branch, or unbounded stack. Positive results must retain those qualifications.
