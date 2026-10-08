C     A small probe of external versus internal A editing into INTEGER.
C     Observed on GNU Fortran 13.3.0; not claimed as portable semantics.
      PROGRAM PROBE
      INTEGER EXT(4),INT(4)
      CHARACTER*16 TEXT
      DATA TEXT/'(I4,I4)         '/
      OPEN(10,STATUS='SCRATCH',FORM='FORMATTED')
      WRITE(10,'(A)') TEXT
      REWIND 10
      READ(10,'(4A4)') EXT
      READ(TEXT,'(4A4)') INT
      WRITE(*,'(A,4A4)') 'external: ',EXT
      WRITE(*,'(A,4A4)') 'internal: ',INT
      CLOSE(10)
      END
