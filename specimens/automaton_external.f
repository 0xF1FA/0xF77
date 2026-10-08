      PROGRAM AUTOM
C     Same transducer as automaton.f, both selection READs use external units.
C     Host transports records and rewinds; FORMAT selects row and symbol cell.
      CHARACTER*8192 TABLE
      CHARACTER*512 ROW
      CHARACTER*32 STATE,SYMBOL
      INTEGER N,J
      READ(5,'(A)') TABLE
      READ(5,'(A)') STATE
      READ(5,*) N
      OPEN(21,STATUS='SCRATCH',FORM='FORMATTED')
      OPEN(22,STATUS='SCRATCH',FORM='FORMATTED')
      WRITE(21,'(A8192)') TABLE
      WRITE(6,'(A)') STATE
      DO 10 J=1,N
        READ(5,'(A)') SYMBOL
        REWIND 21
        READ(21,STATE) ROW
        REWIND 22
        WRITE(22,'(A512)') ROW
        REWIND 22
        READ(22,SYMBOL) STATE
        WRITE(6,'(A)') STATE
   10 CONTINUE
      CLOSE(21)
      CLOSE(22)
      END
