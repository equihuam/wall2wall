"""Installation qualification. Outputs stay in pytest scratch; no product imports."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

import pytest


def run(argv, cwd, **kwargs):
    return subprocess.run(
        argv, cwd=cwd, capture_output=True, text=True, encoding="utf-8",
        errors="replace", timeout=120, **kwargs,
    )


def test_native_toolchain():
    import numpy
    import pandas
    import rasterio
    import sklearn
    from importlib.metadata import version

    assert sys.platform == "win32"
    assert sys.version_info[:2] == (3, 11)
    assert version("snakemake") == "9.27.0"
    for module in (numpy, pandas, rasterio, sklearn):
        assert Path(module.__file__).is_relative_to(Path(sys.prefix))
    assert Path(shutil.which("python")).samefile(sys.executable)
    bash = Path(os.environ["WALL2WALL_BASH"])
    assert bash.is_absolute() and bash.is_file()
    assert "windowsapps" not in str(bash).lower()
    assert Path(shutil.which("bash")).samefile(bash)


@pytest.mark.parametrize("newline", ["\n", "\r\n"], ids=["LF", "CRLF"])
def test_dag(tmp_path, newline):
    work = tmp_path / "ruta con espacios y acentos á"
    work.mkdir()
    for name in ("Snakefile", "raster.py", "summarize.py"):
        source = Path(__file__).with_name(name).read_text(encoding="utf-8")
        (work / name).write_text(source, encoding="utf-8", newline=newline)
    source = work / "entrada.json"
    source.write_text('{"value": 7}', encoding="utf-8")
    command = [sys.executable, "-m", "snakemake", "--cores", "1", "--retries", "0",
               "--scheduler", "greedy", "--printshellcmds"]

    def invoke(**kwargs):
        result = run(command, work, **kwargs)
        assert result.returncode == 0, result.stdout + result.stderr
        return result

    invoke()
    target = work / "resultado final.json"
    raster = work / "mapa pequeño.tif"
    info = json.loads(target.read_text(encoding="utf-8"))
    assert info["mean"] == 7
    assert info["crs"] == 32614
    assert info["shape"] == [4, 4]
    assert info["platform"] == "win32"
    for key in ("raster_python", "summary_python"):
        assert Path(info[key]).samefile(sys.executable)
    before = [p.stat().st_mtime_ns for p in (raster, target)]
    invoke()
    assert [p.stat().st_mtime_ns for p in (raster, target)] == before
    source.write_text('{"value": 9}', encoding="utf-8")
    # Make ordering explicit on filesystems with coarse timestamp resolution.
    newer = max(p.stat().st_mtime_ns for p in (source, raster, target)) + 2_000_000_000
    os.utime(source, ns=(newer, newer))
    invoke()
    assert json.loads(target.read_text(encoding="utf-8"))["mean"] == 9
    raster_mtime = raster.stat().st_mtime_ns
    target.unlink()
    env = dict(os.environ, WALL2WALL_SMOKE_FAIL="1")
    failed = run(command, work, env=env)
    assert failed.returncode != 0
    assert not target.exists()
    assert "23" in failed.stdout + failed.stderr
    invoke()
    assert raster.stat().st_mtime_ns == raster_mtime
    assert json.loads(target.read_text(encoding="utf-8"))["mean"] == 9


def test_bash_arguments_and_error(tmp_path):
    script = tmp_path / "argumentos á.py"
    script.write_text("import json,sys;print(json.dumps(sys.argv[1:]))", encoding="utf-8")
    # POSIX-looking literal requires a selective exclusion at this boundary only.
    env = dict(os.environ, MSYS2_ARG_CONV_EXCL="/literal=")
    result = run(
        [os.environ["WALL2WALL_BASH"], "-c", '"$1" "$2" "dos palabras á" "/literal=/a:/b"',
         "probe", Path(sys.executable).as_posix(), script.as_posix()], tmp_path, env=env,
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == ["dos palabras á", "/literal=/a:/b"]
    result = run([os.environ["WALL2WALL_BASH"], "-c", "set -euo pipefail; false | true"], tmp_path)
    assert result.returncode != 0


def test_windows_file_replace_and_git_lock(tmp_path):
    target = tmp_path / "archivo á.txt"
    new = tmp_path / "nuevo.txt"
    target.write_text("anterior", encoding="utf-8")
    new.write_text("nuevo", encoding="utf-8")
    with target.open("rb"):
        with pytest.raises(PermissionError):
            new.replace(target)
    assert target.read_text(encoding="utf-8") == "anterior"
    new.replace(target)
    assert target.read_text(encoding="utf-8") == "nuevo"
    assert run(["git", "init", "--quiet"], tmp_path).returncode == 0
    lock = tmp_path / ".git/index.lock"
    lock.write_bytes(b"fixture")
    failed = run(["git", "add", "archivo á.txt"], tmp_path)
    assert failed.returncode != 0 and lock.read_bytes() == b"fixture"
    lock.unlink()  # Only our fixture lock; never unlock a live process.
    assert run(["git", "add", "archivo á.txt"], tmp_path).returncode == 0
