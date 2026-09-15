"""Second native Python process entered through explicitly selected Bash."""
import json
import os
from pathlib import Path
import sys

import rasterio

if os.environ.get("WALL2WALL_SMOKE_FAIL") == "1":
    raise SystemExit(23)

with rasterio.open(sys.argv[1]) as src:
    result = {
        "mean": float(src.read(1).mean()),
        "crs": src.crs.to_epsg(),
        "shape": list(src.shape),
        "raster_python": src.tags()["python"],
        "summary_python": sys.executable,
        "platform": sys.platform,
    }
target = Path(sys.argv[2])
temporary = target.with_suffix(".tmp")
temporary.write_text(json.dumps(result), encoding="utf-8")
temporary.replace(target)
