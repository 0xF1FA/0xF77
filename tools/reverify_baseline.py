#!/usr/bin/env python3
"""Run the recovered, unchanged CARBON checks without rewriting old evidence."""
from datetime import datetime, timezone
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def command(argv, **kwargs):
    result = subprocess.run(argv, text=True, capture_output=True,
                            timeout=120, **kwargs)
    return dict(command=argv, returncode=result.returncode,
                stdout=result.stdout, stderr=result.stderr)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--runtime-archive', type=Path)
    args = parser.parse_args()
    fc = shlex.split(os.environ.get('FC', 'gfortran'))
    original = ROOT / 'baseline' / 'carbon'
    evidence = dict(timestamp=datetime.now(timezone.utc).isoformat(),
                    compiler_command=fc,
                    compiler=command([*fc, '--version']),
                    historical_harness_date='2026-10-07',
                    note='Historical harness date is a report label. '
                         'This observation uses the timestamp above. '
                         'Original sources and evidence remain unchanged.')
    if args.runtime_archive:
        evidence['runtime_archive'] = dict(path=str(args.runtime_archive),
                                          sha256=sha(args.runtime_archive))
    with tempfile.TemporaryDirectory(prefix='carbon-baseline-') as td:
        work = Path(td) / 'carbon'
        shutil.copytree(original, work)
        executable = Path(td) / 'link'
        evidence['runtime_probe_build'] = command(
            [*fc, '-std=legacy', '-O2', str(work / 'core' / 'carbon.f'),
             '-o', str(executable)])
        if evidence['runtime_probe_build']['returncode']:
            raise RuntimeError(evidence['runtime_probe_build']['stderr'])
        evidence['runtime_linkage'] = command(['ldd', str(executable)])
        libraries = re.findall(r'libgfortran\S* => (\S+)',
                               evidence['runtime_linkage']['stdout'])
        evidence['loaded_fortran_libraries'] = [
            dict(path=p, sha256=sha(Path(p))) for p in libraries
        ]
        evidence['harness'] = command(
            ['python3', str(work / 'tests' / 'check.py')], cwd=work)
        if evidence['harness']['returncode']:
            raise RuntimeError(evidence['harness']['stderr'])
        evidence['harness_results'] = json.loads(
            (work / 'evidence' / 'results.json').read_text())
        evidence['historical_payload_comparison'] = {
            name: dict(original_sha256=sha(original / 'evidence' / name),
                       observed_sha256=sha(work / 'evidence' / name),
                       identical=(original / 'evidence' / name).read_bytes() ==
                                 (work / 'evidence' / name).read_bytes())
            for name in ['frames.txt', 'spool.dat', 'trace.txt', 'internal-a.txt']
        }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(evidence, indent=2) + '\n')
    print(evidence['harness']['stdout'].strip())
    if not all(item['identical'] for item in
               evidence['historical_payload_comparison'].values()):
        raise SystemExit('Historical payload mismatch; inspect evidence.')
    print('All four historical payloads are byte-for-byte identical.')


if __name__ == '__main__':
    main()
