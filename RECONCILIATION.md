# CARBON and CARBON II: source and evidence reconciliation

Checked 2026-10-08 against draft PR #1, branch
`research/carbon-ii-20261008`, commit
`5db3e835d2d14ceeef414ae5910a565a08a05bbc`. Main contained only LICENSE.
This contribution builds on that research branch and preserves its work on
`research/carbon-reconciled-20261008`. The existing draft PR #1 has not been
modified.

## Two experiments, two causal mechanisms

| Experiment | Mechanism | Empirical scope |
| --- | --- | --- |
| Original CARBON | An INTEGER array is native FORMAT, printable A4 data, numeric feedback and a checkpoint payload. Decimal output changes T102/T108; the moved mark changes the numeric word. | 72-line core, four-state orbit after a transient, ablation and exact restart. GNU 13.3 frontend. The recovered build selects its static 13.3 archive; the original runtime label was incorrect. |
| CARBON II | `READ(TABLE,STATE) ROW` then `READ(ROW,SYMBOL) STATE` selects successor FORMAT programs from records. | Bounded finite transition tables; standard CHARACTER representation. Static GNU 13.3 runtime. |

CARBON II adds useful pattern and parity demonstrations. Its standard CHARACTER
route does not depend on the original numeric-array FORMAT and A-to-INTEGER
extensions. Both use native formatting and records, with an explicit host clock.
Neither experiment establishes a growing tape, unbounded stack, autonomous
general predicate instruction or universality.

## Sources recovered without rewriting the historical observations

`baseline/carbon/` preserves the original core, seed, harness, documentation and
evidence. In particular, `core/carbon.f` retains SHA-256
`1833dd03ec359ab03b4c85d5bbd8dba5bbfd3d34d41390634e7ceaed77ba5dbb`.
The original binary spool is retained; its payload is representation dependent.

`tools/reverify_baseline.py` runs the unchanged harness in a temporary copy. It
records the compiler command, new observation timestamp and runtime linkage,
then compares four observed payloads with the historical files. The old
harness's embedded 2026-10-07 date remains a historical report label.

The historical CARBON II `evidence/results.json` and `source_audit.json` remain
unchanged. New observations have different files:

| Evidence | Result |
| --- | --- |
| `evidence/reverification-2026-10-08.json` | 528/528 traces at each of -O0/-O2/-O3; 1,584 total. All corpus hashes match the historical run. Five external controls per level pass; the full corpus is internal. |
| `evidence/baseline-static13-2026-10-08.json` | 37/37 original checks pass. All four historical payloads match exactly. Static GNU 13.3 archive selected. |
| `evidence/baseline-shared14-2026-10-08.json` | 37/37 original checks pass. All four historical payloads match exactly. Shared libgfortran 14.2 explicitly selected and its resolved path and hash recorded. |

The pattern demo worked in both media. The raw parity input `10110100111`
produced cumulative parity `11011000101`.

The baseline wrapper compiles the actual numeric-plate core for its linkage
probe. It records resolved shared Fortran library paths and binary hashes; the
static observation separately records its selected archive hash. CARBON II's
own executable linkage is recorded in its suite evidence. This prevents an
installed-package list alone from being treated as the executable's binding.

**Runtime attribution correction:** the original report and baseline docs named
installed libgfortran5 14.2 without retaining a linkage witness. The recovered
compiler setup lacks an unversioned shared-library link, so `-lgfortran` resolves
its static 13.3 archive. That earlier runtime label was incorrect. The new
shared-14.2 observation uses an explicit shared-library link and confirms the
actual core's loaded path and hash. Historical docs remain unchanged as evidence;
this file and the revised report provide the correction.

## The inherited comma question now has a reduced causal account

CARBON II reduced the original A-to-INTEGER symptom to ordinary CHARACTER input.
For `AB,CDXYZ` and A8, legacy internal reads produce `AB` followed by spaces;
external reads preserve all eight characters. GNU/f95 controls preserve them in
both media. The comma-vocabulary internal automaton fails in legacy mode; the
colon vocabulary works. Re-verification retained both outcomes.

The inspected GNU 13.3 `libgfortran/io/transfer.c` blob is
`ebad096eeabf7f914751f27711efbee93db9dda6`. Its legacy internal path scans commas
without consulting `sf_read_comma`; its external path checks that flag.
`read.c`, blob `bf2500fc5d050b392144feccbc257ec649dc73b8`, clears the flag during
A editing. This is evidence for the measured runtime, not a rule asserted for
all GNU versions or for standard Fortran.

## Next experiments

1. Build stable writable external record memory. Demonstrate read/overwrite/read
   of a FORMAT-selected cell and credit REWIND, REC=, allocation and record
   creation to the host. Test capacity growth separately.
2. Test another compiler implementation. Separate parse acceptance, descriptor
   behavior, numeric-storage extensions and binary spool compatibility.
3. Investigate compact raw-symbol encodings and comma-driven rewriting while
   retaining full states, controls and failed specimens.

The report in `research/report/` completes the original exploration deliverable
and updates its frontier. Historical sources and current observations remain
separate so an outsider can reproduce either layer.
