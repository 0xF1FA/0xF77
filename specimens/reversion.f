      PROGRAM REVERS
C     Host supplies finite lists. FORMAT reversion supplies record iteration.
      CHARACTER*12 R(3)
      CHARACTER*16 E(3),F
      INTEGER J
      WRITE(R,'("P",2(I1,":"))') 1,2,3,4,5
      DO 10 J=1,3
        WRITE(6,'(A12)') R(J)
   10 CONTINUE
      WRITE(E,'(SP,1P,(E12.3))') 1.0,2.0,3.0
      DO 20 J=1,3
        WRITE(6,'(A16)') E(J)
   20 CONTINUE
C     An independent invocation resets sign/scale defaults.
      WRITE(F,'(E12.3)') 1.0
      WRITE(6,'(A16)') F
      END
