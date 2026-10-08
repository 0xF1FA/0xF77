      PROGRAM LEGACY
C     GNU legacy extensions: numeric A edit and CHARACTER/INTEGER overlap.
C     Instrumentation only uses ICHAR and substrings; it never steers state.
      CHARACTER*4 IN(5),BYTES
      INTEGER WORD,IOS,J,K
      EQUIVALENCE(WORD,BYTES)
      DATA IN /'ABCD','1,23','1 23','1234','(I1,'/
      DO 10 K=1,5
        BYTES='????'
        READ(IN(K),'(A4)',IOSTAT=IOS) WORD
        WRITE(6,'(I1,A1,I6,4I4)') K,'I',IOS,
     +    (ICHAR(BYTES(J:J)),J=1,4)
        OPEN(21,STATUS='SCRATCH',FORM='FORMATTED')
        WRITE(21,'(A4)') IN(K)
        REWIND 21
        BYTES='????'
        READ(21,'(A4)',IOSTAT=IOS) WORD
        WRITE(6,'(I1,A1,I6,4I4)') K,'E',IOS,
     +    (ICHAR(BYTES(J:J)),J=1,4)
        CLOSE(21)
   10 CONTINUE
      END
