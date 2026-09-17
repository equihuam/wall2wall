#!/usr/bin/env bash
set -euo pipefail
repo="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
prefix="$repo/local_state/envs/wall2wall-linux"
test -x "$prefix/bin/python" || { echo 'Missing dedicated Linux interpreter' >&2; exit 2; }
exec env -u PYTHONPATH -u PYTHONHOME -u GDAL_DATA -u PROJ_LIB -u PROJ_DATA -u BASH_ENV \
  PATH="$prefix/bin:/usr/bin:/bin" WALL2WALL_BASH=/bin/bash \
  PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONUTF8=1 \
  OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PROJ_NETWORK=OFF \
  "$prefix/bin/python" "$@"
