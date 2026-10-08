      PROGRAM SYNTAX
C     FORMAT assembles a new grammar from supplied fragments.
C     READ positioning extracts the descriptor from that newly emitted code.
C     Host routes buffers, with no concatenation or substring synthesis.
      CHARACTER*32 SEED,NEXT,SIMPLE,COPY
      CHARACTER*2 DESCR
      CHARACTER*8 R(2),S
      DATA SEED /'("(2(",A2,"),/,A1)")'/
      WRITE(NEXT,SEED) 'I1'
      WRITE(R,NEXT) 4,5,'Z'
      READ(NEXT,'(T4,A2)') DESCR
      WRITE(SIMPLE,'("(",A2,")")') DESCR
      WRITE(S,SIMPLE) 7
      WRITE(COPY,'(A32)') NEXT
      WRITE(6,'(A32)') NEXT
      WRITE(6,'(A8)') R(1)
      WRITE(6,'(A8)') R(2)
      WRITE(6,'(A32)') SIMPLE
      WRITE(6,'(A8)') S
      WRITE(6,'(A32)') COPY
      END
