#!/usr/bin/env python3
"""Falsification checks for the CARBON record machine; no third-party modules."""
import hashlib
import json
import os
from pathlib import Path
import platform
import shlex
import struct
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
FC = shlex.split(os.environ.get('FC', 'gfortran'))
checks = []

def command(args, **kwargs):
    return subprocess.run(args, text=True, capture_output=True, timeout=20, **kwargs)

def check(name, condition, detail=''):
    checks.append({'name': name, 'passed': bool(condition), 'detail': detail})
    if not condition:
        raise AssertionError(name + ': ' + detail)

def run(exe, folder, source, steps, mode=0, frame=0):
    folder.mkdir()
    r = command([str(exe)], cwd=folder,
                input=f'{mode} {steps} {frame}\n{source}\n')
    check(folder.name + ': execution', r.returncode == 0, r.stderr.strip())
    return (folder / 'frames.txt').read_bytes().splitlines(), r.stdout

def payloads(data):
    result = []
    while data:
        n, = struct.unpack('<i', data[:4])
        assert n == 128 and struct.unpack('<i', data[132:136])[0] == n
        result.append(data[4:132])
        data = data[136:]
    return result

with tempfile.TemporaryDirectory(prefix='carbon-check-') as td:
    work = Path(td)
    original = (ROOT / 'core/carbon.f').read_text()
    golden = None
    for opt in ('-O0', '-O2', '-O3'):
        exe = work / ('carbon' + opt[1:])
        flags = ['-std=legacy', '-ffixed-line-length-72', opt, '-fcheck=all']
        built = command(FC + flags + [str(ROOT/'core/carbon.f'), '-o', str(exe)])
        check(opt + ': compile', built.returncode == 0, built.stderr.strip())
        frames, trace = run(exe, work/opt[1:], ROOT/'specimens/feedback.card', 12)
        check(opt + ': record lengths', len(frames) == 13 and
              all(len(x) == 128 for x in frames))
        check(opt + ': four-state orbit', frames[1:5] == frames[5:9]
              == frames[9:13] and len(set(frames[1:5])) == 4)
        check(opt + ': topology and marks',
              [x[28:29] for x in frames[1:5]] == [b'2',b'8',b'8',b'2'] and
              [x[99:109] for x in frames[1:5]] ==
              [b'0010000000',b'0010000000',b'0000000010',b'0000000010'])
        check(opt + ': raw numeric feedback',
              struct.unpack('<i', frames[0][100:104])[0] == 808464432 and
              struct.unpack('<i', frames[1][100:104])[0] == 808464688)
        spool = (work/opt[1:]/'spool.dat').read_bytes()
        check(opt + ': native spool payload', payloads(spool) == frames)
        resumed, _ = run(exe, work/('resume'+opt[1:]),
                         work/opt[1:]/'spool.dat', 8, mode=1, frame=4)
        check(opt + ': restart continuation', resumed == frames[4:13])
        if golden is None:
            golden = frames
        else:
            check(opt + ': optimization independence', frames == golden)
        if opt == '-O2':
            (ROOT/'evidence/trace.txt').write_text(trace)
            (ROOT/'evidence/frames.txt').write_bytes(b'\n'.join(frames)+b'\n')
            (ROOT/'evidence/spool.dat').write_bytes(spool)
    # A control removes the numeric-to-layout feedback; the orbit must vanish.
    control = work/'control.f'
    control.write_text(original.replace(
        'WRITE(11,PLATE,IOSTAT=IOS) PLATE,PLATE(26)',
        'WRITE(11,PLATE,IOSTAT=IOS) PLATE,808464432'))
    exe = work/'control'
    r = command(FC + ['-std=legacy', '-O2', str(control), '-o', str(exe)])
    check('ablation: compile', r.returncode == 0, r.stderr)
    stationary, _ = run(exe, work/'ablation', ROOT/'specimens/feedback.card', 8)
    check('ablation: feedback is causal', len(set(stationary[1:])) == 1)
    # This isolates numeric FORMAT; no Hollerith constant is needed to fail.
    strict = work/'strict.f'
    strict.write_text('      PROGRAM STRICT\n      INTEGER F(2)\n'
                      '      WRITE(*,F) 1\n      END\n')
    r = command(FC + ['-std=f2018', '-pedantic-errors', '-c', str(strict),
                     '-o', str(work/'strict.o')])
    check('strict F2018: rejects integer FORMAT', r.returncode != 0 and
          'FORMAT' in r.stderr, r.stderr.strip())
    # An explicit machine profile must fail closed for eight-byte words.
    exe = work/'wide'
    r = command(FC + ['-std=legacy', '-fdefault-integer-8',
                     str(ROOT/'core/carbon.f'), '-o', str(exe)])
    check('wide-word control: compile', r.returncode == 0, r.stderr)
    r = command([str(exe)], input='0 0 0\nunused\n', cwd=work)
    check('wide-word control: profile rejection', r.returncode == 2 and
          'Unsupported word profile' in r.stdout)
    exe = work/'internal'
    r = command(FC + ['-std=legacy', str(ROOT/'experiments/internal-a.f'),
                     '-o', str(exe)])
    check('internal A probe: compile', r.returncode == 0, r.stderr)
    r = command([str(exe)], cwd=work)
    check('internal A probe: execution', r.returncode == 0, r.stderr)
    (ROOT/'evidence/internal-a.txt').write_text(r.stdout)
    # Record a phenomenon, not a requirement imposed on future compilers.
    observed = {'internal_a_probe': r.stdout,
                'internal_a_differs': r.stdout.splitlines()[0][10:] !=
                                      r.stdout.splitlines()[1][10:]}

version = command(FC+['--version']).stdout.splitlines()[0]
report = {'date':'2026-10-07', 'compiler':version,
          'platform': platform.machine() + ' / ' + platform.system(),
          'profile': 'ASCII, little endian, default INTEGER=4 bytes',
          'compiler_flags':'-std=legacy -ffixed-line-length-72 -fcheck=all',
          'optimizations':['-O0','-O2','-O3'], 'checks':checks,
          'passed':sum(x['passed'] for x in checks),
          'phenomena':observed,
          'source_sha256':hashlib.sha256((ROOT/'core/carbon.f').read_bytes()).hexdigest(),
          'spool_sha256':hashlib.sha256((ROOT/'evidence/spool.dat').read_bytes()).hexdigest()}
(ROOT/'evidence/results.json').write_text(json.dumps(report,indent=2)+'\n')
print(f"{report['passed']}/{len(checks)} checks passed; {version}")
