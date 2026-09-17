"""
## engines.py

## Descripción
Construye regresores opcionales LightGBM y XGBoost sin ajustar, con parámetros
explícitos de CPU y un hilo para su entrega a las APIs existentes de modelado.

## Precondiciones
Python 3.11 y el motor solicitado disponible en el entorno activo. Valida sus
argumentos antes de importarlo; no requiere tablas, capas ni CRS.

## Resultados
make_regressor devuelve intacto el estimador sklearn construido. No ejecuta fit,
instala dependencias ni escribe archivos; importar este módulo sólo usa stdlib.

## Notas relevantes
Las cotas de extras expresan API requerida, no compatibilidad real cualificada.
Sólo la ausencia exacta del motor recibe un diagnóstico del extra; errores
transitivos o nativos se propagan. La cualificación real queda para M004-S04.
=============================================================================
"""
import math
from numbers import Integral, Real


def make_regressor(engine, *, n_estimators, random_state, max_depth=None, learning_rate=0.1):
    """Construct an unfitted optional CPU regressor after validating all arguments."""
    if not isinstance(engine, str) or engine not in ("lightgbm", "xgboost"):
        raise ValueError("engine must be lightgbm or xgboost")
    for name, value in (("n_estimators", n_estimators), ("max_depth", max_depth)):
        if name == "max_depth" and value is None:
            continue
        if isinstance(value, bool) or not isinstance(value, Integral) or value <= 0:
            raise ValueError(f"{name} must be a positive integer" + (" or None" if name == "max_depth" else ""))
    if isinstance(random_state, bool) or not isinstance(random_state, Integral) or not 0 <= random_state <= 2147483647:
        raise ValueError("random_state must be an integer in 0..2147483647")
    if (isinstance(learning_rate, bool) or not isinstance(learning_rate, Real)
            or not 0 < learning_rate <= 1 or not math.isfinite(learning_rate)):
        raise ValueError("learning_rate must be finite and real in (0, 1]")
    try:
        if engine == "lightgbm":
            from lightgbm import LGBMRegressor
            constructor = LGBMRegressor
        else:
            from xgboost import XGBRegressor
            constructor = XGBRegressor
    except ModuleNotFoundError as error:
        if error.name != engine:
            raise
        raise ImportError(
            f"Optional engine {engine} is absent; provision wall2wall[{engine}] "
            "in the active Python environment before requesting this engine. No automatic installation."
        ) from error
    common = {"n_estimators": int(n_estimators), "random_state": int(random_state),
              "learning_rate": float(learning_rate), "n_jobs": 1}
    if engine == "lightgbm":
        return constructor(**common, max_depth=-1 if max_depth is None else int(max_depth),
                           objective="regression", boosting_type="gbdt", device_type="cpu",
                           deterministic=True, force_col_wise=True)
    return constructor(**common, max_depth=0 if max_depth is None else int(max_depth),
                       objective="reg:squarederror", booster="gbtree", tree_method="hist", device="cpu")
