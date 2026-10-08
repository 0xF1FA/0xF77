      PROGRAM BSTORE
C     Bounded shift operations, not an extensible stack/queue implementation.
C     READ/WRITE descriptors move substrings; host never slices or indexes.
      CHARACTER*4 OLD,PUSHED,POPPED,QUEUE
      CHARACTER*3 PART
      CHARACTER*1 ITEM
      DATA OLD /'abc_'/
      READ(OLD,'(A3)') PART
      WRITE(PUSHED,'(A1,A3)') 'X',PART
      READ(PUSHED,'(A1,A3)') ITEM,PART
      WRITE(POPPED,'(A3,1H_)') PART
      WRITE(6,'(A4)') PUSHED
      WRITE(6,'(A1)') ITEM
      WRITE(6,'(A4)') POPPED
      OLD='abcd'
      READ(OLD,'(A1,A3)') ITEM,PART
      WRITE(QUEUE,'(A3,A1)') PART,'X'
      WRITE(6,'(A1)') ITEM
      WRITE(6,'(A4)') QUEUE
      END
