# GNU word4 profile

Observed: GNU Fortran 13.3.0 (Ubuntu 13.3.0-6ubuntu2~24.04.1), dynamically linked
to libgfortran5 14.2.0-4ubuntu2~24.04.1, x86-64 Linux, 2026-10-07.

Build switches: `-std=legacy -ffixed-line-length-72 -fcheck=all`, with each of
`-O0`, `-O2`, `-O3` checked. The library package and compiler have different
versions; runtime behavior must be attributed to this combination.

| Mechanism | Classification |
|---|---|
| Fixed form, formatted external records, T positioning, I editing | Standard F77 mechanisms |
| Output H edit descriptor | Standard F77, deleted from Fortran 95 |
| Integer array used as FORMAT | Historical compatibility extension |
| A editing into/out of INTEGER | Historical Hollerith compatibility extension |
| Hollerith DATA constant used in profile check | Historical compatibility extension |
| Physical little-endian four-byte words | Explicit machine assumption |
| Four-byte unformatted record markers | Measured GNU runtime configuration |

There is no `-std=f77` mode. Legacy acceptance is not a conformance certificate.
The driver checks the numeric value of the Hollerith word `1000`; a build with
eight-byte default integers is rejected rather than silently producing garbage.

The single-record specimen consumes 32 raw words and one numeric feedback word.
Every successful tick must emit exactly one record. The supplied test checks
that its length is 128 bytes. Full validation of arbitrary user-written formats
is not implemented. A negative I/O status after the first output record is used
to confirm end-of-file, and positive statuses abort the driver.

Modern Fortran can deliberately reproduce the representation bridge with
`TRANSFER`, CHARACTER formats and quoted literals. That is a useful control
implementation, not evidence that modern Fortran lacks the computational power.
The legacy object itself is simultaneously numeric storage and native format.
