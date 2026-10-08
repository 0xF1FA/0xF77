#!/usr/bin/env python3
"""Compile and demonstrate the FORMAT transducer; Python assembles/displays only."""
import argparse
import os
import shlex
import tempfile
from pathlib import Path
from run import ROOT, assemble, command

p=argparse.ArgumentParser()
p.add_argument('--example',choices=['pattern','parity'],default='pattern')
p.add_argument('--word')
p.add_argument('--external',action='store_true')
a=p.parse_args()
fc=shlex.split(os.environ.get('FC','gfortran'))
if a.example=='parity':
    word=a.word if a.word is not None else '10110100111'
    if any(c not in '01' for c in word):p.error('parity accepts binary digits')
    if a.external:p.error('raw parity specimen uses internal records')
    source=ROOT/'specimens'/'parity.f'
    data=str(len(word))+'\n'+'\n'.join(word)+'\n'
else:
    word=a.word if a.word is not None else 'xaabxb'
    if any(c not in 'abx' for c in word):p.error('pattern alphabet is a, b, x')
    source=ROOT/'specimens'/('automaton_external.f' if a.external
                             else 'automaton.f')
    data,_,programs=assemble([[1,0,0],[1,2,0],[2,2,2]],
                            ['abx'.index(c) for c in word],structural=True)
with tempfile.TemporaryDirectory(prefix='carbon-demo-') as tmp:
    exe=Path(tmp)/'machine'
    built=command([*fc,'-std=legacy','-O2',str(source),'-o',str(exe)])
    if built['returncode']:raise SystemExit(built['stderr'])
    out=command([str(exe)],data=data,cwd=tmp)
    if out['returncode']:raise SystemExit(out['stderr'])
print('Input:',word)
if a.example=='parity':
    print('Cumulative parity:', ''.join(out['stdout'].splitlines()))
else:
    # Display decoding is outside the Fortran state-transition mechanism.
    labels=['START','LAST_A','SEEN_AB']
    decode=dict(zip(programs,labels))
    for j,code in enumerate(out['stdout'].splitlines()):
        print('start' if j==0 else word[j-1], '=>',decode[code],code.rstrip())
