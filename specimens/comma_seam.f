      PROGRAM COMMA
C     Standard CHARACTER, identical bytes and A8, only medium changes.
C     Run with -std=legacy, -std=gnu and -std=f95; preserve every outcome.
      CHARACTER*8 RECORD,I,E
      INTEGER SI,SE
      DATA RECORD /'AB,CDXYZ'/
      READ(RECORD,'(A8)',IOSTAT=SI) I
      OPEN(21,STATUS='SCRATCH',FORM='FORMATTED')
      WRITE(21,'(A8)') RECORD
      REWIND 21
      READ(21,'(A8)',IOSTAT=SE) E
      CLOSE(21)
      WRITE(6,'(I6,1X,A8)') SI,I
      WRITE(6,'(I6,1X,A8)') SE,E
      END
