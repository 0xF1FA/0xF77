# CARBON / 0xF77

A printout rewrites the FORMAT that will print it next.

```sh
sh run.sh
python3 tests/check.py
```

Requires Linux, gfortran and (for checks only) Python 3. The observed profile is
GNU Fortran 13.3.0 with Ubuntu libgfortran5 14.2.0, x86-64, ASCII and four-byte
little-endian default INTEGER. `FC=/path/to/gfortran sh run.sh` selects a compiler.
Other compiler/runtime combinations are experiments, not verified support.

The engine is 72 lines of fixed-form Fortran. It uses F77-era GNU compatibility
extensions and is **not strict ANSI FORTRAN 77**. Read `dialects/gnu-word4.md`.

The plate is 32 integer words. It is used as all of the following:

* a native runtime FORMAT;
* the data printed by its own `32A4` descriptor;
* a numeric feedback source (`PLATE(26)`);
* the complete payload of a native unformatted checkpoint record.

There is no opcode parser or application arithmetic on the machine state. The
host drives ticks and I/O. Native formatting does the rewrite:

```fortran
      REWIND 11
      WRITE(11,PLATE) PLATE,PLATE(26)
      REWIND 11
      READ(11,'(32A4)') PLATE
```

The actual driver also checks I/O failures and the one-record contract.
Source/destination records are separate while the format is being evaluated.

Inspect `specimens/feedback.card` without trimming spaces. This is a 128-column
experimental plate, not a claim that historical cards had 128 columns. Its
first 58 columns are:

```text
(32A4,T100,10H0000000000,T102,1H1,T20,I10,T20,9H00000,T10)
```

`T102` stamps `1` into the ten-column field at columns 100-109. `I10` prints the
numeric value of word 26 over columns 20-29. The final H literal repairs columns
20-28, leaving the last decimal digit in column 29: the last digit of `T102`.
The next plate therefore changes to `T108`. The moved mark changes word 26.

After a transient, the full state has period four. Two consecutive printouts
have the same visible mark but different instructions. The mark alone is not
the state.

`build/demo/frames.txt` holds exact textual states, including the seed.
`build/demo/spool.dat` holds native binary states. `evidence/` contains the run
made on 2026-10-07, with 37 checks and a compiler/runtime seam reproducer.

## Resume from a fossil

From the project directory, after `sh run.sh`:

```sh
mkdir -p build/resumed
cd build/resumed
printf '1 8 4\n../demo/spool.dat\n' | ../carbon
```

The input header is `MODE STEPS FRAME`; the next line is a pathname. MODE 0
loads a textual plate. MODE 1 loads a zero-based frame from a binary spool.
Outputs are `frames.txt` and `spool.dat` in the current directory. Use a fresh
directory to retain earlier runs. The spool is portable only within a matching
representation/runtime profile; it is not a crash-safe archival database.

## Intervene

Start by changing the mark literal `1H1` to `1H2` in a copied seed. Keep the
record width and grammar intact. Compare entire states and orbit lengths.
Then inspect `PHENOMENA.md` and the accompanying research report.

The local specimen runner is for deliberate experiments with trusted plates.
It is not a sandbox or remote execution service. No external compiler or
network process is invoked by the running Fortran machine.

Historical neighbors include Bratley and Millo's 1972 Fortran self-reproducing
program and Carlini's IOCCC 2020 printf machine. CARBON is a proposed synthesis,
not a claim to the first quine, formatter computer or universal machine.
