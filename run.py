#!/usr/bin/env python3
"""Reproducible CARBON II experiments. Python is assembly and verification only.

It never runs in the Fortran transition path. FC may contain compiler arguments.
Results preserve exact commands, sources (in specimens), inputs, and outputs.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
from pathlib import Path
import platform
import random
import shlex
import subprocess
import tempfile
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent


def command(argv, *, data=None, cwd=None):
    p = subprocess.run(argv, input=data, text=True, capture_output=True,
                       cwd=cwd, timeout=15)
    return dict(command=argv, returncode=p.returncode,
                stdout=p.stdout, stderr=p.stderr)


def selector(position, width, nested=False, separator=':'):
    # Colon is a real descriptor, harmless while a list item remains.
    # This independently tested vocabulary avoids comma bytes in code cells;
    # the original comma-containing vocabulary is retained in seam tests.
    s = (f"(T{position:04d}{separator}1(A{width:04d}))" if nested
         else f"(T{position:04d}{separator}A{width:04d})")
    assert len(s) <= 32 and 0 < position <= 9999 and width <= 9999
    return s.ljust(32)


def assemble(transitions, word, initial=0, structural=False, separator=':'):
    k = len(transitions[0])
    assert 1 <= k <= 16 and len(transitions) * k * 32 <= 8192
    programs = [selector(1 + s * k * 32, k * 32,
                         structural and bool(s % 2), separator)
                for s in range(len(transitions))]
    table = ''.join(programs[t] for row in transitions for t in row)
    symbols = [selector(1 + a * 32, 32, separator=separator) for a in word]
    data = '\n'.join([table, programs[initial], str(len(word)), *symbols])+'\n'
    state = initial
    expected = [programs[state]]
    for a in word:
        state = transitions[state][a]
        expected.append(programs[state])
    return data, expected, programs


def run_suite(fc):
    evidence = dict(timestamp=datetime.now(timezone.utc).isoformat(),
                    machine=platform.machine(), system=platform.platform(),
                    compiler=command([*fc, '--version']), runs=[],
                    inherited_baseline='The original CARBON II run inherited '
                    'the baseline because its source was unavailable. The '
                    'recovered baseline is now in baseline/carbon; separately '
                    'dated re-verification is in evidence/baseline-*.json. '
                    'This suite tests CARBON II only.')
    evidence['installed_packages'] = command(['dpkg-query','-W',
        'gcc-13-x86-64-linux-gnu','libgfortran5'])
    evidence['runtime_binding_note'] = (
        'The original research FC selected the Ubuntu libgfortran-13-dev '
        '13.3.0-6ubuntu2~24.04.1 static archive with -static-libgfortran. '
        'Installed libgfortran5 alone does not identify a static runtime. '
        'Inspect compiler command and runtime_linkage before comparing runs.')
    failures = []
    specimens = sorted((ROOT/'specimens').glob('*.f'))
    with tempfile.TemporaryDirectory(prefix='carbon-ii-') as tmp:
        tmp = Path(tmp)
        for opt in ['-O0', '-O2', '-O3']:
            batch = dict(optimization=opt, specimens=[], automata=[])
            binaries = {}
            for source in specimens:
                executable = tmp/f'{source.stem}{opt}'
                build = command([*fc, '-std=legacy', opt, str(source),
                                 '-o', str(executable)])
                batch['specimens'].append(dict(name=source.stem,
                    source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                    build=build))
                if build['returncode']:
                    failures.append(f'{opt} compile {source.name}')
                else:
                    binaries[source.stem] = executable
            if len(binaries) != len(specimens):
                evidence['runs'].append(batch)
                continue
            batch['runtime_linkage'] = command(['ldd',str(binaries['automaton'])])

            def execute(name, data='', expected=None):
                out = command([str(binaries[name])], data=data, cwd=tmp)
                witness = dict(name=name, input=data, expected=expected,
                               observed=out)
                batch.setdefault('observations', []).append(witness)
                if out['returncode'] or (expected is not None and
                        out['stdout'].splitlines() != expected):
                    failures.append(f'{opt} {name}')
                return out['stdout'].splitlines()

            execute('colon', expected=['A       ', 'AB7     ', 'AB0     ',
                                      'A       '])
            execute('indirect', expected=['Z', '0009abcdXefghijk', 'd',
                                         '        X       '])
            execute('syntax', expected=['(2(I1),/,A1)'.ljust(32),
                '45'.ljust(8), 'Z'.ljust(8), '(I1)'.ljust(32),
                '7'.ljust(8), '(2(I1),/,A1)'.ljust(32)])
            execute('record_address', expected=['D','A'])
            execute('legacy_format', expected=['CODE'])
            execute('reversion')
            execute('legacy_medium')
            execute('medium')
            execute('comma_seam')
            execute('typed')
            execute('bounded_store',expected=['Xabc','X','abc_','a','bcdX'])
            execute('direct_medium',expected=['abXdefgh','abXdefgh'])

            word = '10110100111'
            parity = []
            q = 0
            for bit in word:
                q ^= int(bit)
                parity.append(str(q))
            execute('parity', str(len(word))+'\n'+'\n'.join(word)+'\n', parity)

            representative = [
                ('F0-constant', [[0]], [0]*4, False),
                ('F2-toggle', [[1],[0]], [0]*8, False),
                ('F5-parity', [[0,1],[1,0]], [1,0,1,1,0,1], False),
                ('F6-ab-recognizer', [[1,0,0],[1,2,0],[2,2,2]],
                 [2,0,0,1,2,1], True),
                ('F6-5-state-3-symbol', [[1,4,2],[3,1,0],[4,2,1],
                 [0,2,4],[2,3,0]], [0,1,2,2,1,0,1,0,2], True)]
            for label, table, symbols, structural in representative:
                data, expected, _ = assemble(table, symbols,
                                             structural=structural)
                out = command([str(binaries['automaton'])], data=data, cwd=tmp)
                ok = out['returncode']==0 and out['stdout'].splitlines()==expected
                batch['automata'].append(dict(name=label, transitions=table,
                    word=symbols, input=data, expected=expected, observed=out,
                    passed=ok))
                if not ok: failures.append(f'{opt} {label}')
                external = command([str(binaries['automaton_external'])],
                                   data=data,cwd=tmp)
                eok = (external['returncode']==0 and
                       external['stdout'].splitlines()==expected)
                batch['automata'][-1]['external_observed']=external
                batch['automata'][-1]['external_passed']=eok
                if not eok: failures.append(f'{opt} external {label}')

            # All 16 binary transition tables; all words of length 0..4.
            corpus = []
            for cells in itertools.product(range(2), repeat=4):
                table = [list(cells[:2]),list(cells[2:])]
                for length in range(5):
                    for word in itertools.product(range(2), repeat=length):
                        corpus.append((table,list(word)))
            rng = random.Random(771977)
            for n,k in [(3,3),(5,4),(7,3),(8,4)]:
                for _ in range(8):
                    corpus.append(([[rng.randrange(n) for _ in range(k)]
                        for _ in range(n)], [rng.randrange(k) for _ in range(64)]))
            passed = 0
            corpus_fails = []
            for table, symbols in corpus:
                data, expected, _ = assemble(table, symbols, structural=True)
                out = command([str(binaries['automaton'])], data=data, cwd=tmp)
                if out['returncode']==0 and out['stdout'].splitlines()==expected:
                    passed += 1
                else:
                    corpus_fails.append(dict(transitions=table,word=symbols,
                        input=data,expected=expected,observed=out))
            batch['exhaustive_and_seeded'] = dict(total=len(corpus), passed=passed,
                sha256=hashlib.sha256(json.dumps(corpus).encode()).hexdigest(),
                failures=corpus_fails)
            if corpus_fails: failures.append(f'{opt} finite-table corpus')

            # Two controlled interventions using exactly the same specimen.
            table = [[0,1],[1,0]]
            symbols = [1,0,1,1,0,1]
            data,expected,programs = assemble(table,symbols)
            lines = data.splitlines()
            lines[0] = programs[0]*4
            freeze = command([str(binaries['automaton'])],
                             data='\n'.join(lines)+'\n',cwd=tmp)
            frozen_expected = [programs[0]] * (len(symbols)+1)
            assert freeze['stdout'].splitlines()==frozen_expected
            data_constant,constant_expected,_ = assemble(table,[0]*len(symbols))
            constant = command([str(binaries['automaton'])],
                               data=data_constant,cwd=tmp)
            assert constant['stdout'].splitlines()==constant_expected
            batch['ablations']=dict(frozen_transition_payload=freeze,
                constant_symbol=constant,original_expected=expected,
                frozen_expected=frozen_expected,constant_expected=constant_expected)

            programs = [selector(1+32*i,32) for i in range(4)]
            atable=''.join(programs[i] for i in [0,1,0,1])
            btable=''.join(programs[i] for i in [3,2,2,3])
            composition_data='\n'.join([atable,btable,programs[2]])+'\n'
            execute('composition', composition_data,
                [programs[i] for i in [2,0,3,1,2,0,3,1,2]])
            for label,t in [('A',[0,1,0,1]),('B',[3,2,2,3])]:
                d,e,_ = assemble([[i] for i in t],[0]*5,initial=2)
                out = command([str(binaries['automaton'])],data=d,cwd=tmp)
                assert out['stdout'].splitlines()==e
                batch.setdefault('composition_controls',[]).append(
                    dict(name=label,expected=e,observed=out))

            probes = [
                ('integer','(I4)',12),('zero-suppressed','(I1.0)',0),
                ('nonzero-suppressed','(I1.0)',1),('overflow','(I1)',12),
                ('sign-plus','(SP,I4)',12),('sign-minus','(SS,I4)',12),
                ('absolute','(T5,I1)',7),('relative','(3X,I1)',7),
                ('overwrite','(I1,TL1,1HX)',7),('literal','(2HOK,I1)',7),
                ('nested','(2(I1))',7),('native-colon','(I1,:,1HX)',7),
                ('unconditional-suffix','(I1,1HX)',7),
                ('binary','(B8.8)',7),('octal','(O4.4)',7),
                ('hex','(Z4.4)',15),('minimum-width','(I0)',123),
                ('general-minimum','(G0)',123),('unlimited','(*(I1))',7),
                ('zero-repeat','(0(I1))',7),('variable-expression','(I<3>)',7),
                ('Q-descriptor','(Q)',7),('omit-comma','(1HX I1)',7),
                ('dollar','(I1,$)',7),('long-position','(T81,I1)',7)]
            pinput=str(len(probes))+'\n'+''.join(f'{f}\n{v}\n' for _,f,v in probes)
            lines=execute('probe',pinput)
            parsed=[]
            for (label,fmt,val),line in zip(probes,lines):
                parsed.append(dict(name=label,format=fmt,value=val,
                    internal_status=int(line[:6]),external_status=int(line[6:12]),
                    internal_bytes=line[13:93],external_bytes=line[94:174]))
            batch['format_probes']=parsed
            assert len(lines)==len(probes)
            # Same bytes and same source, change only the compiler dialect.
            batch['dialect_medium_matrix']=[]
            for dialect in ['legacy','gnu','f95']:
                seam_bin=tmp/f'seam-{dialect}{opt}'
                sb=command([*fc,f'-std={dialect}',opt,
                    str(ROOT/'specimens'/'comma_seam.f'),'-o',str(seam_bin)])
                sr=command([str(seam_bin)],cwd=tmp)
                batch['dialect_medium_matrix'].append(dict(
                    dialect=dialect,build=sb,comma_seam=sr))
                for specimen in ['automaton','automaton_external']:
                    xbin=tmp/f'{specimen}-{dialect}{opt}'
                    xb=command([*fc,f'-std={dialect}',opt,
                        str(ROOT/'specimens'/f'{specimen}.f'),'-o',str(xbin)])
                    for sep in [',',':']:
                        d,e,_=assemble([[0,1],[1,0]],[1,0,1,1],separator=sep)
                        xr=command([str(xbin)],data=d,cwd=tmp)
                        batch['dialect_medium_matrix'][-1].setdefault(
                            'automata',[]).append(dict(name=specimen,
                            separator=sep,build=xb,input=d,expected=e,observed=xr,
                            matched=xr['returncode']==0 and
                                xr['stdout'].splitlines()==e))
            evidence['runs'].append(batch)

        # Strict later-standard compilation is supporting evidence, not an
        # F77 certification. Runtime string descriptors require manual dating.
        standard=[]
        for source in specimens:
            out=command([*fc,'-std=f95','-pedantic-errors',str(source),
                         '-o',str(tmp/f'{source.stem}-strict')])
            standard.append(dict(name=source.stem,build=out))
        evidence['strict_f95_compile']=standard
    evidence['failures']=failures
    return evidence


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,default=ROOT/'evidence'/'results.json')
    args=parser.parse_args()
    fc=shlex.split(os.environ.get('FC','gfortran'))
    results=run_suite(fc)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(results,indent=2)+'\n')
    for batch in results['runs']:
        corpus=batch.get('exhaustive_and_seeded',{})
        print(batch['optimization'],corpus.get('passed',0),'/',corpus.get('total',0))
    print('Failures:',results['failures'])
    raise SystemExit(bool(results['failures']))


if __name__=='__main__': main()
