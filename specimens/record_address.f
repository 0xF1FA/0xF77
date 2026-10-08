      PROGRAM RADDR
C     Host creates/repositions file. FORMAT determines the selected record.
C     Literal 3 is an externally supplied address; no host skip loop.
      CHARACTER*32 SELECT
      CHARACTER*1 TOKEN
      INTEGER ADDRESS
      OPEN(21,STATUS='SCRATCH',FORM='FORMATTED')
      WRITE(21,'(A1)') 'A','B','C','D','E'
      ADDRESS=3
      WRITE(SELECT,'("(",I2,"(/),A1)")') ADDRESS
      REWIND 21
      READ(21,SELECT) TOKEN
      WRITE(6,'(A1)') TOKEN
      REWIND 21
      READ(21,'(A1)') TOKEN
      WRITE(6,'(A1)') TOKEN
      CLOSE(21)
      END
