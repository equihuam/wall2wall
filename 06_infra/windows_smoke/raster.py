"""Tiny deterministic native-library probe; not the Wall2Wall implementation."""
import json
from pathlib import Path
import sys

import numpy as np
import rasterio
from rasterio.transform import from_origin
from sklearn.ensemble import RandomForestRegressor

assert sys.platform == "win32" and sys.version_info[:2] == (3, 11)
value = json.loads(Path(snakemake.input[0]).read_text(encoding="utf-8"))["value"]
x = np.arange(16, dtype="float32").reshape(-1, 1)
model = RandomForestRegressor(n_estimators=4, random_state=17, n_jobs=1)
model.fit(x, np.full(16, value))
data = model.predict(x).astype("float32").reshape(4, 4)
with rasterio.Env(GDAL_CACHEMAX=128 * 1024 * 1024):
    with rasterio.open(
        snakemake.output[0], "w", driver="GTiff", width=4, height=4,
        count=1, dtype="float32", crs="EPSG:32614",
        transform=from_origin(400000, 2200000, 10, 10), nodata=-9999,
    ) as dst:
        dst.write(data, 1)
        dst.update_tags(python=sys.executable)
