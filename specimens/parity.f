      PROGRAM PARITY
C     Raw binary input. Host clocks and routes; every transition uses I/O.
C     Overlapping fields at columns 10 and 11 of TABLE yield 01 or 10.
C     BIT selects column 10/11 of ROW; RESULT generates next state FORMAT.
      CHARACTER*12 TABLE
      CHARACTER*11 ROW
      CHARACTER*10 STATE
      CHARACTER*10 SYMBOL
      CHARACTER*2 PAIR
      CHARACTER*1 BIT,RESULT
      INTEGER N,J
      DATA TABLE /'         010'/
      DATA STATE /'(T10,A2)'/
      READ(5,*) N
      DO 10 J=1,N
        READ(5,'(A1)') BIT
        READ(TABLE,STATE) PAIR
        WRITE(ROW,'(T10,A2)') PAIR
        WRITE(SYMBOL,'("(T1",A1,",A1)")') BIT
        READ(ROW,SYMBOL) RESULT
        WRITE(STATE,'("(T1",A1,",A2)")') RESULT
        WRITE(6,'(A1)') RESULT
   10 CONTINUE
      END
