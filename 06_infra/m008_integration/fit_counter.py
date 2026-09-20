"""
## fit_counter.py

## Descripción
Cuenta entradas fit por proceso y fase mediante reservas persistentes SQLite.
Instrumenta las clases públicas admitidas sin contar árboles internos de RF.

## Precondiciones
Base externa creada explícitamente, fase reservada y variables locales de ejecución.
Modo qualification permite sólo dobles declarados; science requiere admisión externa.

## Resultados
Registra intentos y terminaciones; rechaza exceso, ausencia, duplicados e interrupción.
La entrada --child conserva aislamiento Python y ejecuta archivo, código o módulo.
Para archivos verifica identidad y habilita sólo su directorio para imports hermanos.

## Notas relevantes
No inicia fits por sí mismo. Contar Pipeline y sus pasos es intencional; envolver
la misma clase dos veces no duplica eventos. No instala paquetes ni mata procesos.
=============================================================================
"""
import contextlib
import functools
import hashlib
import os
from pathlib import Path
import runpy
import sqlite3
import sys
import uuid


@contextlib.contextmanager
def connection(path):
    path = Path(path).resolve()
    if not path.is_file():
        raise ValueError("counter missing")
    db = sqlite3.connect(path.as_uri() + "?mode=rw", uri=True, timeout=10)
    try:
        db.execute("BEGIN IMMEDIATE")
        yield db
        db.commit()
    except BaseException:
        db.rollback()
        raise
    finally:
        db.close()


def create(path, maximum, mode="qualification"):
    if type(maximum) is not int or maximum < 0 or mode not in ("qualification", "science"):
        raise ValueError("invalid counter policy")
    path = Path(path)
    with path.open("xb"):
        pass
    db = sqlite3.connect(path)
    try:
        db.executescript("CREATE TABLE policy(cap INTEGER, mode TEXT);"
            "CREATE TABLE phases(name TEXT PRIMARY KEY, cap INTEGER, status TEXT);"
            "CREATE TABLE calls(token TEXT PRIMARY KEY, phase TEXT, pid INTEGER, class TEXT, test TEXT, status TEXT);")
        db.execute("INSERT INTO policy VALUES (?,?)", (maximum, mode)); db.commit()
    finally:
        db.close()


def reserve(path, phase, maximum):
    if type(maximum) is not int or maximum < 0 or not phase:
        raise ValueError("invalid reservation")
    with connection(path) as db:
        cap = db.execute("SELECT cap FROM policy").fetchone()[0]
        if db.execute("SELECT 1 FROM phases WHERE name=?", (phase,)).fetchone():
            raise ValueError("reservation consumed")
        used = db.execute("SELECT COALESCE(SUM(cap),0) FROM phases").fetchone()[0]
        if used + maximum > cap or db.execute("SELECT 1 FROM phases WHERE status!='finished'").fetchone():
            raise ValueError("overbudget or previous phase pending")
        db.execute("INSERT INTO phases VALUES (?,?,'reserved')", (phase, maximum))


def enter(path, phase, label, fake=False):
    token = uuid.uuid4().hex
    with connection(path) as db:
        mode = db.execute("SELECT mode FROM policy").fetchone()[0]
        if mode == "qualification" and not fake:
            raise ValueError("real fits forbidden in qualification")
        row = db.execute("SELECT cap,status FROM phases WHERE name=?", (phase,)).fetchone()
        if row is None or row[1] != "reserved":
            raise ValueError("missing or closed phase")
        count = db.execute("SELECT COUNT(*) FROM calls WHERE phase=?", (phase,)).fetchone()[0]
        if count >= row[0]:
            raise ValueError("fit budget exceeded before fit")
        db.execute("INSERT INTO calls VALUES (?,?,?,?,?,'pending')", (token, phase, os.getpid(), label,
            os.environ.get("PYTEST_CURRENT_TEST", "child")))
    return token


def leave(path, token, status):
    if status not in ("passed", "failed"):
        raise ValueError("invalid completion")
    with connection(path) as db:
        cursor = db.execute("UPDATE calls SET status=? WHERE token=? AND status='pending'", (status, token))
        if cursor.rowcount != 1:
            raise ValueError("missing or duplicate completion")


def finish(path, phase, expected):
    with connection(path) as db:
        row = db.execute("SELECT cap,status FROM phases WHERE name=?", (phase,)).fetchone()
        calls = db.execute("SELECT status FROM calls WHERE phase=?", (phase,)).fetchall()
        if row is None or row[1] != "reserved" or len(calls) != expected or any(x[0] == "pending" for x in calls):
            raise ValueError("missing or interrupted fit evidence")
        db.execute("UPDATE phases SET status='finished' WHERE name=?", (phase,))
    return expected


def wrap(cls, path, phase, fake=False):
    original = cls.fit
    if getattr(original, "_wall2wall_counter", None) == (str(path), phase):
        return
    @functools.wraps(original)
    def counted(self, *args, **kwargs):
        token = enter(path, phase, cls.__module__ + "." + cls.__name__, fake=fake)
        try:
            result = original(self, *args, **kwargs)
        except BaseException:
            leave(path, token, "failed")
            raise
        leave(path, token, "passed")
        return result
    counted._wall2wall_counter = (str(path), phase)
    cls.fit = counted


def activate():
    path, phase = os.environ.get("WALL2WALL_FIT_DB"), os.environ.get("WALL2WALL_FIT_PHASE")
    if not path or not phase:
        raise ValueError("counter environment missing")
    with connection(path) as db:
        row = db.execute("SELECT status FROM phases WHERE name=?", (phase,)).fetchone()
        if row is None or row[0] != "reserved":
            raise ValueError("phase not reserved")
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.dummy import DummyRegressor
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import StandardScaler
    for cls in (RandomForestRegressor, DummyRegressor, Pipeline, StandardScaler):
        wrap(cls, path, phase)


class CollectionCounter:
    def pytest_collection_modifyitems(self, session, config, items):
        path, phase = os.environ["WALL2WALL_FIT_DB"], os.environ["WALL2WALL_FIT_PHASE"]
        for module in {item.module for item in items}:
            for name in ("SpyRegressor", "SpyTransformer", "Memorizer", "LocalTransformer"):
                cls = getattr(module, name, None)
                if cls is not None:
                    wrap(cls, path, phase)


def bootstrap(directory, database, phase):
    directory = Path(directory)
    directory.mkdir()
    helper = Path(__file__).resolve()
    digest = hashlib.sha256(helper.read_bytes()).hexdigest()
    code = ("import os, runpy, hashlib\nfrom pathlib import Path\n"
            "try:\n"
            " p=Path(os.environ['WALL2WALL_COUNTER_HELPER'])\n"
            " assert hashlib.sha256(p.read_bytes()).hexdigest()==os.environ['WALL2WALL_COUNTER_SHA256']\n"
            " runpy.run_path(str(p))['activate']()\n"
            "except BaseException:\n os._exit(86)\n")
    (directory / "sitecustomize.py").write_text(code, encoding="utf-8")
    return {"WALL2WALL_FIT_DB": str(Path(database).resolve()), "WALL2WALL_FIT_PHASE": phase,
            "WALL2WALL_COUNTER_HELPER": str(helper), "WALL2WALL_COUNTER_SHA256": digest,
            "PYTHONPATH": str(directory.resolve())}


def script_path(name):
    path = Path(name).absolute()
    for part in (path, *path.parents):
        if part.is_symlink() or (part.exists() and getattr(part.stat(), "st_file_attributes", 0) & 0x400):
            raise ValueError("linked child script path")
    if not path.is_file():
        raise ValueError("child script missing")
    return path.resolve(strict=True)


def child(argv):
    if not sys.flags.isolated or hashlib.sha256(Path(__file__).read_bytes()).hexdigest() != os.environ.get("WALL2WALL_COUNTER_SHA256"):
        raise ValueError("isolated verified helper required")
    activate()
    while argv and argv[0] in ("-I", "-B", "-u"):
        argv = argv[1:]
    if not argv:
        raise ValueError("child command missing")
    if argv[0] in ("-c", "-m") and len(argv) < 2:
        raise ValueError("child command argument missing")
    if argv[0] == "-c":
        code = argv[1]; sys.argv = ["-c", *argv[2:]]
        exec(compile(code, "<counter-child>", "exec"), {"__name__": "__main__"})
    elif argv[0] == "-m":
        sys.argv = argv[1:]; runpy.run_module(argv[1], run_name="__main__", alter_sys=True)
    else:
        if argv[0].startswith("-"):
            raise ValueError("unsupported child option")
        script = script_path(argv[0])
        if hashlib.sha256(script.read_bytes()).hexdigest() != os.environ.get("WALL2WALL_CHILD_SCRIPT_SHA256"):
            raise ValueError("child script changed")
        previous = sys.path[:]
        try:
            sys.path.insert(0, str(script.parent))
            sys.argv = [str(script), *argv[1:]]
            runpy.run_path(str(script), run_name="__main__")
        finally:
            sys.path[:] = previous


if __name__ == "__main__":
    if sys.argv[1:2] != ["--child"]:
        raise SystemExit("only explicit --child is supported")
    child(sys.argv[2:])
