      PROGRAM SEAM
C     A falsifiable control: direct output ends after a backward tab.
C     Does its implicit end padding damage the following record?
      CHARACTER*80 ORIGINAL,NEIGHBOR,PATCH
      CHARACTER*32 CODE
      INTEGER J
      ORIGINAL=REPEAT('A',80)
      CODE='(T0001:A32:A32:A64:A1)'
      OPEN(21,STATUS='SCRATCH',ACCESS='DIRECT',FORM='FORMATTED',
     +     RECL=80)
      DO 10 J=1,3
        WRITE(21,'(A80)',REC=J) ORIGINAL
   10 CONTINUE
      WRITE(21,'(A80:T1:A32:T33:A1:T49:I8)',REC=1)
     +     ORIGINAL,CODE,'1',1234
      READ(21,'(A80)',REC=2) NEIGHBOR
      WRITE(6,'(A80)') NEIGHBOR
      DO 20 J=1,3
        WRITE(21,'(A80)',REC=J) ORIGINAL
   20 CONTINUE
      WRITE(PATCH,'(A80:T1:A32:T33:A1:T49:I8)')
     +     ORIGINAL,CODE,'1',1234
      WRITE(21,'(A80)',REC=1) PATCH
      READ(21,'(A80)',REC=2) NEIGHBOR
      WRITE(6,'(A80)') NEIGHBOR
      CLOSE(21)
      END
