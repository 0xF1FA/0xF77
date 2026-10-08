      PROGRAM INDIR
C     Address is READ from record; I editing manufactures the selector.
C     No host subscript, substring, arithmetic, or IF uses the address.
C     Whole-record copy and overwrite happen in one WRITE to preserve memory.
      CHARACTER*16 OLD,NEW
      CHARACTER*32 SELECT,STORE
      CHARACTER*1 TOKEN
      INTEGER ADDRESS
      DATA OLD /'0009abcdZefghijk'/
      READ(OLD,'(I4)') ADDRESS
      WRITE(SELECT,'("(T",I4.4,",A1)")') ADDRESS
      READ(OLD,SELECT) TOKEN
      WRITE(STORE,'("(A,T",I4.4,",A1)")') ADDRESS
      WRITE(NEW,STORE) OLD,'X'
      WRITE(6,'(A1)') TOKEN
      WRITE(6,'(A16)') NEW
C     Freeze selector: data unchanged, the address-dependent retrieval stops.
      READ(OLD,'(T8,A1)') TOKEN
      WRITE(6,'(A1)') TOKEN
C     Separate WRITE does not preserve the unmentioned cells.
      NEW=OLD
      WRITE(NEW,'(T9,A1)') 'X'
      WRITE(6,'(A16)') NEW
      END
