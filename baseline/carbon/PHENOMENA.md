# Measured phenomena

## E01: decimal ink changes its own layout

Status: observed on the profile in `dialects/gnu-word4.md`.
Record: `evidence/trace.txt`, `frames.txt`, `results.json`.

`A4` absorption of `0000` gives 808464432; `0100` gives 808464688 on this profile.
Native `I10` places the last digit into a `T10d` descriptor. H overprinting
repairs the other nine positions touched by the numeric output. A four-state
orbit follows. Replacing the feedback word by a fixed integer removes the orbit.
No undefined signed overflow or conflicting argument aliases are involved.

Architectural consequence: formatting, word representation and record state
form a closed causal loop. Possible compositions: other mark glyphs, numeric
taps, multiple repair stencils, larger records, and multiple records with a
revised driver contract. Those larger constructions are not yet implemented.

## E02: the native spool is a runnable state fossil

Status: observed. Each record payload is exactly the 128 plate bytes, framed
by four-byte little-endian GNU record markers in this configuration. Loading
frame 4 in a fresh process and taking eight transitions reproduces frames 4-12
of an uninterrupted run. The absolute host tick counter is not part of state.

Architectural consequence: execution can be inspected, paused and branched at
a record boundary. No claim of cross-compiler interchange, crash consistency,
atomic commit, or arbitrary-process checkpointing follows.

## E03: internal and external A input disagree

Status: observed, cause unresolved. Run `experiments/internal-a.f`.
The same text `(I4,I4)` is read using `4A4` into INTEGER arrays, once from an
external record and once from an internal CHARACTER file. The external path
preserves punctuation; the internal path produces `(I4 I` followed by blanks.
The full CARBON plate consequently fails as a FORMAT after the internal route.

This is a result for a nonstandard transfer on one compiler/runtime combination.
It is not a statement that standard CHARACTER internal I/O is broken. A future
runtime may differ; the test records this observation without requiring it.

Next experiment: inspect libgfortran's legacy A/numeric input path, minimize
comma-position cases, and compare a second runtime before assigning a cause.

## Evidence boundary

37 checks passed. The successful legacy run, the causal ablation, and the
strict-F2018 rejection are different pieces of evidence. None establishes
Turing completeness, a new theorem, historical priority, all-compiler behavior,
or a useful large-scale programming model.
