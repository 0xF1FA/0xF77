      PROGRAM AUTOM
C     Host: fixed clock, input transport, logging; no state arithmetic.
C     FORMAT: select state row, then input-symbol cell containing next code.
C     Medium: TABLE and ROW carry an assembled finite transition relation.
C     Representation: standard CHARACTER, not the earlier Hollerith seam.
      CHARACTER*8192 TABLE
      CHARACTER*512 ROW
      CHARACTER*32 STATE,SYMBOL
      INTEGER N,J
      READ(5,'(A)') TABLE
      READ(5,'(A)') STATE
      READ(5,*) N
      WRITE(6,'(A)') STATE
      DO 10 J=1,N
        READ(5,'(A)') SYMBOL
        READ(TABLE,STATE) ROW
        READ(ROW,SYMBOL) STATE
        WRITE(6,'(A)') STATE
   10 CONTINUE
      END
