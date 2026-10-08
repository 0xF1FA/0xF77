      PROGRAM COMPOS
C     A and B are separately idempotent maps; alternate their FORMAT reads.
C     Host fixes A/B order. It does not select a map using current state.
      CHARACTER*128 A,B
      CHARACTER*32 S
      INTEGER J
      READ(5,'(A)') A
      READ(5,'(A)') B
      READ(5,'(A)') S
      WRITE(6,'(A32)') S
      DO 10 J=1,4
        CALL STEP(A,S)
        WRITE(6,'(A32)') S
        CALL STEP(B,S)
        WRITE(6,'(A32)') S
   10 CONTINUE
      END
      SUBROUTINE STEP(TABLE,STATE)
      CHARACTER*128 TABLE
      CHARACTER*32 STATE,NEXT
C     Distinct NEXT avoids overwriting the active FORMAT in its own READ.
      READ(TABLE,STATE) NEXT
      STATE=NEXT
      END
