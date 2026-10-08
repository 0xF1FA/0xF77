      PROGRAM PROBE
C     Each request: runtime FORMAT then integer value. No host value branch.
C     One WRITE on each medium; report IOSTAT and blank-padded physical output.
      CHARACTER*160 FMT
      CHARACTER*80 IREC,EREC
      INTEGER VALUE,SI,SE,N,J
      READ(5,*) N
      DO 10 J=1,N
        READ(5,'(A)') FMT
        READ(5,*) VALUE
        IREC='UNWRITTEN'
        EREC='UNWRITTEN'
        WRITE(IREC,FMT,IOSTAT=SI) VALUE
        OPEN(21,STATUS='SCRATCH',FORM='FORMATTED')
        WRITE(21,FMT,IOSTAT=SE) VALUE
        REWIND 21
        IF(SE.EQ.0) READ(21,'(A80)',IOSTAT=SE) EREC
        CLOSE(21)
        WRITE(6,'(2I6,1X,A80,1X,A80)') SI,SE,IREC,EREC
   10 CONTINUE
      END
