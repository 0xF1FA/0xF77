#!/bin/sh
set -eu
cd "$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
mkdir -p build/demo
"${FC:-gfortran}" -std=legacy -ffixed-line-length-72 -O2 \
  -fcheck=all core/carbon.f -o build/carbon
cd build/demo
printf '0 8 0\n../../specimens/feedback.card\n' | ../carbon
printf '\nSaved build/demo/frames.txt and build/demo/spool.dat\n'
