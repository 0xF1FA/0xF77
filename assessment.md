# Computational assessment

Demonstrated: a record transducer with a parsed FORMAT program, bounded I/O-list
traversal, within-record positioning, persistent record contents and programs
that are replaced between I/O invocations. With a fixed host pump, it implements
any assembled finite transition table within the specimen's buffer limits.

The automaton source has an 8,192-character transition record, 512-character
row buffer, and 32-character program cells. The assembler permits at most 16
symbols and requires `states * symbols * 32 <= 8192`. Generality concerns the
transition relation within that capacity. A larger family of buffers is not a
demonstration of memory growing during one execution.

The strongest direct control is conditional termination on I/O-list exhaustion.
Numeric edits also have value-dependent behavior, such as `I1.0` suppressing
zero and a narrow field producing stars. Those transformations do not provide a
general descriptor-level `IF value THEN program A ELSE program B` instruction.
Table selection supplies that behavior in the record-feedback machine.

Reversion repeats a format group across records and retains editing modes.
The supplied list bounds the iteration. Ordinary Fortran DO supplies the clock
for inter-invocation feedback; it must be credited to the host.

Numeric fields can become addresses: READ extracts an address, WRITE's I edit
encodes it into a T descriptor, and a subsequent READ retrieves the selected
character. WRITE can preserve a record by copying it and overwriting a position
in one invocation. A separate WRITE blanks unmentioned cells. Slash groups can
select a later external record after a host REWIND. Direct-access REC= and
REWIND/BACKSPACE are host I/O controls, not edit descriptors.

Literal and A editing can assemble FORMAT syntax, including nested groups and
slash descriptors. A positioning read extracts a fragment and another WRITE
builds a simpler program. This demonstrates grammar construction and copying
supplied fragments. It does not demonstrate autonomous grammar invention,
recursive subroutine calls, or a host-independent reproducer.

Two individually idempotent maps can form a recurrent coupled system. The
specimen fixes the alternation schedule in the host and leaves all state
transitions in FORMAT-selected record fields. It establishes composition, not
spontaneous synchronization or an ecosystem of independently scheduled agents.

The GNU 13.3 runtime source explains the comma seam: the legacy internal-read
path scans for commas without the character-read comma-control check used by
the external path. This happens even with CHARACTER, broadening the inherited
integer-storage observation. The scope is the measured runtime and flags.
Expressive equivalence of different media is not proved; one working common
finite-state construction prevents this seam alone from proving a difference
in computational class.

Known model: a finite-state record transducer with bounded spatial memory and
an external clock. String-rewriting or tape-machine comparisons remain research
targets. Universality is neither demonstrated nor refuted for all possible
extensions of CARBON. In this fixed-capacity, bounded-input specimen, the total
machine is finite.
