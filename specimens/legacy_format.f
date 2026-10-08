      PROGRAM LFORMAT
C     Hollerith bytes are both integer storage and executable FORMAT grammar.
C     One-shot representation probe; it does not redo the known feedback loop.
      INTEGER FMT(1),WORD
      CHARACTER*4 BYTES,OUT
      EQUIVALENCE(WORD,BYTES)
      DATA FMT /4H(A4)/
      BYTES='CODE'
      WRITE(OUT,FMT) WORD
      WRITE(6,'(A4)') OUT
      END
