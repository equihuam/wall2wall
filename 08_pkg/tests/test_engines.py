"""
## test_engines.py

## Descripción
Comprueba el contrato offline de motores opcionales: importación perezosa,
validación previa, argumentos de constructor y propagación de errores.

## Precondiciones
Pytest y Python 3.11; el lanzador prepara scratch externo. Los imports opcionales
se interceptan con dobles mínimos, sin requerir motores instalados ni datos.

## Resultados
Exige importación ligera en proceso fresco y mapeos exactos sin llamadas fit.
Comprueba ausencia exacta frente a fallos transitivos, nativos o de constructor.

## Notas relevantes
Cero ajustes nuevos. Los dobles sólo acreditan el contrato local, no clone,
fit, predict ni compatibilidad con motores reales, pendiente de M004-S04.
=============================================================================
"""
import builtins
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

import pytest

PACKAGE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE / "src"))
from wall2wall.engines import make_regressor
sys.path.pop(0)


def intercept(monkeypatch, handler):
    original = builtins.__import__
    def guarded(name, *args, **kwargs):
        if name.split(".")[0] in {"lightgbm", "xgboost"}:
            return handler(name)
        return original(name, *args, **kwargs)
    monkeypatch.setattr(builtins, "__import__", guarded)


def test_fresh_lightweight_import(tmp_path):
    code = '''
import importlib.abc
import sys
from pathlib import Path
blocked = {"lightgbm", "xgboost", "numpy", "pandas", "rasterio", "sklearn", "joblib", "snakemake"}
class Reject(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split(".")[0] in blocked:
            raise AssertionError("Unexpected import: " + fullname)
sys.meta_path.insert(0, Reject())
sys.path.insert(0, sys.argv[1])
import wall2wall
import wall2wall.engines
assert Path(wall2wall.engines.__file__).resolve() == Path(sys.argv[1]) / "wall2wall/engines.py"
assert callable(wall2wall.engines.make_regressor)
assert not blocked.intersection(name.split(".")[0] for name in sys.modules)
'''
    result = subprocess.run([sys.executable, "-I", "-B", "-c", code, str(PACKAGE / "src")],
                            cwd=tmp_path, capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize("engine", ["lightgbm", "xgboost"])
@pytest.mark.parametrize("depth", [None, 3])
def test_constructor_contract(monkeypatch, engine, depth):
    calls, imports = [], []
    returned = SimpleNamespace(fit=lambda *a, **k: pytest.fail("factory must not fit"))
    def constructor(**kwargs):
        calls.append(kwargs)
        return returned
    def requested(name):
        imports.append(name)
        assert name == engine
        return SimpleNamespace(**{("LGBMRegressor" if engine == "lightgbm" else "XGBRegressor"): constructor})
    intercept(monkeypatch, requested)
    for seed, rate in ((0, .1), (2147483647, 1)):
        result = make_regressor(engine, n_estimators=1, random_state=seed, max_depth=depth, learning_rate=rate)
        assert result is returned
        expected = {"n_estimators": 1, "random_state": seed, "learning_rate": rate, "n_jobs": 1}
        if engine == "lightgbm":
            expected.update(max_depth=-1 if depth is None else depth, objective="regression", boosting_type="gbdt",
                            device_type="cpu", deterministic=True, force_col_wise=True)
        else:
            expected.update(max_depth=0 if depth is None else depth, objective="reg:squarederror",
                            booster="gbtree", tree_method="hist", device="cpu")
        assert calls[-1] == expected
    default = make_regressor(engine, n_estimators=5, random_state=17)
    assert default is returned
    assert calls[-1]["learning_rate"] == .1
    assert calls[-1]["max_depth"] == (-1 if engine == "lightgbm" else 0)
    assert imports == [engine] * 3


@pytest.mark.parametrize("engine", ["lightgbm", "xgboost"])
def test_validation_before_import(monkeypatch, engine):
    intercept(monkeypatch, lambda name: pytest.fail("validation must precede import"))
    valid = {"engine": engine, "n_estimators": 3, "random_state": 17}
    cases = {"engine": ["unknown", "LightGBM", None, [], True],
             "n_estimators": [0, -1, 1.5, True, False, None, "2"],
             "random_state": [-1, 2147483648, 1.5, True, None, "17"],
             "max_depth": [0, -1, 1.5, True, False, "3"],
             "learning_rate": [0, -1, 1.01, True, False, None, "0.1", float("nan"), float("inf"), 1j]}
    for field, values in cases.items():
        for value in values:
            with pytest.raises(ValueError, match=field):
                make_regressor(**{**valid, field: value})
    with pytest.raises(TypeError, match="unexpected keyword argument 'callbacks'"):
        make_regressor(**valid, callbacks=[])
    with pytest.raises(TypeError, match="n_estimators"):
        make_regressor(engine, random_state=17)


@pytest.mark.parametrize("engine", ["lightgbm", "xgboost"])
def test_missing_engine(monkeypatch, engine):
    error = ModuleNotFoundError("absent", name=engine)
    def absent(name):
        assert name == engine
        raise error
    intercept(monkeypatch, absent)
    with pytest.raises(ImportError) as caught:
        make_regressor(engine, n_estimators=2, random_state=17)
    assert caught.value.__cause__ is error
    assert str(caught.value) == (f"Optional engine {engine} is absent; provision wall2wall[{engine}] "
                                "in the active Python environment before requesting this engine. No automatic installation.")


@pytest.mark.parametrize("engine", ["lightgbm", "xgboost"])
def test_errors_preserved(monkeypatch, engine):
    for error in (ModuleNotFoundError("transitive", name="dependency"),
                  ModuleNotFoundError("submodule", name=engine + ".native"),
                  ImportError("DLL load failed"), OSError("native library failed")):
        def broken(name):
            assert name == engine
            raise error
        intercept(monkeypatch, broken)
        with pytest.raises(type(error)) as caught:
            make_regressor(engine, n_estimators=2, random_state=17)
        assert caught.value is error
    # A constructor failure must not be translated into a missing-package message.
    error = ModuleNotFoundError("constructor failure", name=engine)
    def constructor(**kwargs):
        raise error
    intercept(monkeypatch, lambda name: SimpleNamespace(
        **{("LGBMRegressor" if engine == "lightgbm" else "XGBRegressor"): constructor}))
    with pytest.raises(ModuleNotFoundError) as caught:
        make_regressor(engine, n_estimators=2, random_state=17)
    assert caught.value is error
