C     CARBON: GNU legacy Hollerith record machine. Not strict F77.
C     stdin: MODE STEPS FRAME, then an input pathname on its own line.
C     MODE 0 reads text; MODE 1 reads FRAME (zero-based) from a spool.
C     Physics: ASCII, little endian, four-byte default INTEGER.
      PROGRAM CARBON
      INTEGER PLATE(32),KEY,MODE,STEPS,FRAME,J,K,IOS
      CHARACTER*256 PATH
      CHARACTER*128 LINE
      DATA KEY/4H1000/
      IF (KEY.NE.808464433) THEN
         WRITE(*,'(A)') 'Unsupported word profile; use default INTEGER4'
         STOP 2
      END IF
      READ(*,*,IOSTAT=IOS) MODE,STEPS,FRAME
      IF (IOS.NE.0) STOP 3
      IF (MODE.LT.0.OR.MODE.GT.1) STOP 3
      IF (STEPS.LT.0.OR.STEPS.GT.10000) STOP 3
      IF (FRAME.LT.0.OR.FRAME.GT.10000) STOP 3
      READ(*,'(A)',IOSTAT=IOS) PATH
      IF (IOS.NE.0) STOP 3
      IF (MODE.EQ.0) THEN
         OPEN(10,FILE=PATH,STATUS='OLD',IOSTAT=IOS)
         IF (IOS.NE.0) STOP 4
         READ(10,'(32A4)',IOSTAT=IOS) PLATE
         IF (IOS.NE.0) STOP 4
      ELSE
         OPEN(10,FILE=PATH,STATUS='OLD',FORM='UNFORMATTED',
     1        IOSTAT=IOS)
         IF (IOS.NE.0) STOP 4
         DO 10 J=0,FRAME
            READ(10,IOSTAT=IOS) PLATE
            IF (IOS.NE.0) STOP 4
   10    CONTINUE
      END IF
      CLOSE(10)
      OPEN(11,STATUS='SCRATCH',FORM='FORMATTED')
      OPEN(20,FILE='spool.dat',STATUS='UNKNOWN',
     1     FORM='UNFORMATTED')
      OPEN(21,FILE='frames.txt',STATUS='UNKNOWN')
      REWIND 20
      REWIND 21
      WRITE(*,'(A)') 'tick | word 26 | next format | columns 100:109'
      DO 100 K=0,STEPS
         WRITE(20) PLATE
         WRITE(21,'(32A4)') PLATE
         WRITE(LINE,'(32A4)') PLATE
         WRITE(*,'(I4,1X,I10,1X,A,1X,A)')
     1        K,PLATE(26),LINE(1:58),LINE(100:109)
         IF (K.LT.STEPS) THEN
C           This is the whole transition. No opcode decoder, arithmetic
C           on the state, EQUIVALENCE, COMMON, or assigned GO TO.
            REWIND 11
            WRITE(11,PLATE,IOSTAT=IOS) PLATE,PLATE(26)
            IF (IOS.NE.0) THEN
               WRITE(*,'(A,I8)') 'FORMAT write failed: ',IOS
               STOP 5
            END IF
            ENDFILE 11
            REWIND 11
            READ(11,'(32A4)',IOSTAT=IOS) PLATE
            IF (IOS.NE.0) STOP 6
C           The specimen contract is exactly one output record.
            READ(11,'(A)',IOSTAT=IOS) LINE
            IF (IOS.GE.0) STOP 7
         END IF
  100 CONTINUE
      ENDFILE 20
      ENDFILE 21
      CLOSE(11)
      CLOSE(20)
      CLOSE(21)
      END
