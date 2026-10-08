      PROGRAM DIRECT
C     Direct-access record addressing is explicitly host REC=, not FORMAT.
C     Within the selected record, FORMAT positions and overwrites fields.
      CHARACTER*8 I,E
      WRITE(I,'(A,T3,A1)') 'abcdefgh','X'
      OPEN(21,STATUS='SCRATCH',ACCESS='DIRECT',FORM='FORMATTED',
     +  RECL=8)
      WRITE(21,'(A,T3,A1)',REC=1) 'abcdefgh','X'
      READ(21,'(A8)',REC=1) E
      CLOSE(21)
      WRITE(6,'(A8)') I
      WRITE(6,'(A8)') E
      END
