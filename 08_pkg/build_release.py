"""
## build_release.py

## Descripción
Construye wheel, sdist y complemento de fuentes del workflow con inventario explícito.
Materializa soporte de infraestructura sólo en staging externo y conserva logs.

## Precondiciones
Python >=3.11, build/setuptools/wheel instalados; fuentes enumeradas completas.
--output-dir debe ser nuevo y externo al árbol fuente, sin solapamiento.

## Resultados
Artefactos locales y release-manifest.json con tamaños, SHA-256 y versiones.
Staging y logs permanecen en el destino, incluso tras fallo; no instala paquetes.

## Notas relevantes
Sin red ni aislamiento que resuelva dependencias. Límite de artefactos 16 MiB.
El wheel contiene sólo API; el workflow requiere entorno fijo y árbol complementario.
=============================================================================
"""
import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tarfile
import tomllib

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parent


def identity(path):
    data = path.read_bytes()
    return {"size": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def inputs():
    inventory = json.loads((PACKAGE / "release-files.json").read_text())
    if inventory["schema"] != "wall2wall.release-files/1":
        raise ValueError("unsupported release inventory")
    result = {}
    support = ROOT / "06_infra" if PACKAGE.name == "08_pkg" else PACKAGE / "release-support/06_infra"
    for group, base, prefix in (("package", PACKAGE, "08_pkg"), ("support", support, "06_infra")):
        for name in inventory[group]:
            relative = PurePosixPath(name)
            if relative.is_absolute() or ".." in relative.parts or "\\" in name or str(relative) != name:
                raise ValueError("unsafe inventory path")
            source = base / name
            if source.is_symlink() or not source.is_file() or not source.resolve().is_relative_to(base.resolve()):
                raise ValueError("missing or unsafe input: " + name)
            key = prefix + "/" + name
            if key in result:
                raise ValueError("duplicate release input")
            result[key] = source
    return result


def build(output):
    output = Path(output)
    resolved = output.resolve()
    source_root = ROOT if PACKAGE.name == "08_pkg" else PACKAGE
    if os.path.lexists(output) or resolved.is_relative_to(source_root) or source_root.is_relative_to(resolved):
        raise ValueError("output-dir must be new and external to source tree")
    sources = inputs()
    for source in sources.values():
        if resolved.is_relative_to(source.resolve()) or source.resolve().is_relative_to(resolved):
            raise ValueError("output overlaps release inputs")
    frozen = {name: identity(path) for name, path in sources.items()}
    resolved.mkdir(parents=True, exist_ok=False)
    stage = resolved / "staging"
    for name, source in sources.items():
        relative = name.removeprefix("08_pkg/") if name.startswith("08_pkg/") else "release-support/" + name
        dest = stage / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, dest)
    env = dict(os.environ, PIP_NO_INDEX="1", PIP_DISABLE_PIP_VERSION_CHECK="1", PIP_NO_CACHE_DIR="1", PYTHONDONTWRITEBYTECODE="1")
    command = [sys.executable, "-I", "-B", "-m", "build", "--no-isolation", "--sdist", "--wheel", "--outdir", str(resolved), str(stage)]
    with (resolved / "build.log").open("w") as log:
        subprocess.run(command, cwd=resolved, env=env, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=120)
    bundle = resolved / "workflow-source.tar.gz"
    with tarfile.open(bundle, "w:gz") as archive:
        for name, source in sorted(sources.items()):
            info = archive.gettarinfo(str(source), arcname=name)
            info.uid = info.gid = 0
            info.uname = info.gname = ""
            info.mtime = 0
            with source.open("rb") as stream:
                archive.addfile(info, stream)
    project = tomllib.loads((stage / "pyproject.toml").read_text())["project"]
    artifacts = [resolved / ("wall2wall-" + project["version"] + suffix) for suffix in ("-py3-none-any.whl", ".tar.gz")] + [bundle]
    sizes = {p.name: identity(p) for p in artifacts}
    if sum(v["size"] for v in sizes.values()) > 16 * 1024**2:
        raise ValueError("release artifacts exceed 16 MiB")
    if frozen != {name: identity(path) for name, path in sources.items()}:
        raise ValueError("release sources changed during build")
    manifest = {"schema":"wall2wall.release/1", "name":project["name"], "version":project["version"],
                "requires_python":project["requires-python"], "files":sizes, "inputs":frozen,
                "tools":{name:importlib.metadata.version(name) for name in ("build","setuptools","wheel")},
                "python":sys.version.split()[0], "command":"python 08_pkg/build_release.py --output-dir <new-external-directory>",
                "workflow":"sources only; fixed environment required; qualify_linux.py excluded"}
    (resolved / "release-manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    return resolved


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    try:
        build(args.output_dir)
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        parser.exit(2, "release: " + str(error) + "\n")


if __name__ == "__main__":
    main()
