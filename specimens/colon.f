      PROGRAM COLON
C     Presence/exhaustion conditional, not a predicate on a numeric value.
      CHARACTER*8 A,B,C,D
      WRITE(A,'("A",:,"B",I1)')
      WRITE(B,'("A",:,"B",I1)') 7
      WRITE(C,'("A",:,"B",I1)') 0
      WRITE(D,'("A",I1)')
      WRITE(6,'(A8)') A
      WRITE(6,'(A8)') B
      WRITE(6,'(A8)') C
      WRITE(6,'(A8)') D
      END
