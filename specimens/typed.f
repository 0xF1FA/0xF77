      PROGRAM TYPED
C     Typed descriptor probes. Helpers change only the record medium.
      CHARACTER*4 REC(2),C4
      CHARACTER*2 C2
      CHARACTER*5 HEAD
      CHARACTER*1 TREC
      CHARACTER*1 A,B,C
      INTEGER X,Y
      LOGICAL L,M
      DATA REC /'1 2 ','3 4 '/
      DATA HEAD /'ABCDE'/,TREC /'T'/
      CALL INTGET('1 2 ','(BN,I4)')
      CALL INTGET('1 2 ','(BZ,I4)')
      CALL INTGET('bad ','(I4)')
      CALL REALGET('0123','(F4.2)')
      CALL REALGET('0123','(2P,F4.2)')
      CALL REALPUT('(F8.2)',2.5)
      CALL REALPUT('(E12.3)',2.5)
      CALL REALPUT('(D12.3)',2.5)
      CALL REALPUT('(G12.3)',2.5)
      CALL REALPUT('(SP,F8.2)',2.5)
      READ(REC,'(BZ,(I4))') X,Y
      WRITE(6,'(A,2I6)') 'BZ_REVERSION ',X,Y
      READ(REC(1),'(I4)') X
      WRITE(6,'(A,I6)') 'BLANK_RESET ',X
      C4='ABCD'
      READ(C4,'(A4)') C2
      WRITE(6,'(A,A2)') 'A_TRUNCATE ',C2
      READ(C2,'(A2)') C4
      WRITE(6,'(A,A4)') 'A_PAD ',C4
      READ(HEAD,'(T3,A1,TL2,A1,TR1,A1)') A,B,C
      WRITE(6,'(A,3A1)') 'HEAD ',A,B,C
      READ(HEAD,'(TL8,A1)') A
      WRITE(6,'(A,A1)') 'LEFT_CLAMP ',A
      READ(TREC,'(L1)') L
      OPEN(21,STATUS='SCRATCH',FORM='FORMATTED')
      WRITE(21,'(A1)') 'T'
      REWIND 21
      READ(21,'(L1)') M
      CLOSE(21)
      WRITE(6,'(A,2L1)') 'LOGICAL ',L,M
      END
      SUBROUTINE INTGET(REC,FMT)
      CHARACTER*(*) REC,FMT
      INTEGER X,Y,SI,SE
      X=-999
      Y=-999
      READ(REC,FMT,IOSTAT=SI) X
      OPEN(21,STATUS='SCRATCH',FORM='FORMATTED')
      WRITE(21,'(A)') REC
      REWIND 21
      READ(21,FMT,IOSTAT=SE) Y
      CLOSE(21)
      WRITE(6,'(A,1X,4I8)') FMT,SI,X,SE,Y
      END
      SUBROUTINE REALGET(REC,FMT)
      CHARACTER*(*) REC,FMT
      REAL X,Y
      INTEGER SI,SE
      X=-999.0
      Y=-999.0
      READ(REC,FMT,IOSTAT=SI) X
      OPEN(21,STATUS='SCRATCH',FORM='FORMATTED')
      WRITE(21,'(A)') REC
      REWIND 21
      READ(21,FMT,IOSTAT=SE) Y
      CLOSE(21)
      WRITE(6,'(A,1X,2I6,2F12.6)') FMT,SI,SE,X,Y
      END
      SUBROUTINE REALPUT(FMT,X)
      CHARACTER*(*) FMT
      CHARACTER*16 I,E
      REAL X
      INTEGER SI,SE
      WRITE(I,FMT,IOSTAT=SI) X
      OPEN(21,STATUS='SCRATCH',FORM='FORMATTED')
      WRITE(21,FMT,IOSTAT=SE) X
      REWIND 21
      READ(21,'(A16)') E
      CLOSE(21)
      WRITE(6,'(A,1X,2I6,1X,A16,1X,A16)') FMT,SI,SE,I,E
      END
