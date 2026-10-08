      PROGRAM MEDIUM
C     Matched bytes/FORMAT, different record medium. Report status and bytes.
      CHARACTER*3 SHORT
      CHARACTER*8 OUT,RAW
      CHARACTER*1 ONE
      INTEGER IOS,A,B
      WRITE(SHORT,'(A4)',IOSTAT=IOS) 'ABCD'
      WRITE(6,'(A,I6)') 'INTERNAL_WRITE_OVERFLOW ',IOS
      OPEN(21,STATUS='SCRATCH',FORM='FORMATTED')
      WRITE(21,'(A4)',IOSTAT=IOS) 'ABCD'
      WRITE(6,'(A,I6)') 'EXTERNAL_WRITE ',IOS
      REWIND 21
      READ(21,'(A8)') RAW
      WRITE(6,'(A8)') RAW
      CLOSE(21)
      SHORT='7'
      A=-9
      B=-9
      READ(SHORT,'(I2,I2)',IOSTAT=IOS) A,B
      WRITE(6,'(A,3I6)') 'INTERNAL_PAD ',IOS,A,B
      OPEN(21,STATUS='SCRATCH',FORM='FORMATTED')
      WRITE(21,'(A1)') '7'
      REWIND 21
      A=-9
      B=-9
      READ(21,'(I2,I2)',IOSTAT=IOS) A,B
      WRITE(6,'(A,3I6)') 'EXTERNAL_PAD ',IOS,A,B
      CLOSE(21)
      ONE='K'
      READ(ONE,'(A8)',IOSTAT=IOS) OUT
      WRITE(6,'(A,I6,1X,A8)') 'INTERNAL_WIDE_A ',IOS,OUT
      OPEN(21,STATUS='SCRATCH',FORM='FORMATTED')
      WRITE(21,'(A1)') 'K'
      REWIND 21
      READ(21,'(A8)',IOSTAT=IOS) OUT
      WRITE(6,'(A,I6,1X,A8)') 'EXTERNAL_WIDE_A ',IOS,OUT
      CLOSE(21)
      END
