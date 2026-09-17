```diff
HEAD diff filtered to current-round paths; this is not a prior-round delta.
diff --git a/08_pkg/src/wall2wall/__init__.py b/08_pkg/src/wall2wall/__init__.py
index 3574471..5519367 100644
--- a/08_pkg/src/wall2wall/__init__.py
+++ b/08_pkg/src/wall2wall/__init__.py
@@ -4,14 +4,15 @@
 ## Descripción
 Define el punto de importación ligero de Wall2Wall. La armonización de capas
 está disponible mediante una importación explícita de wall2wall.spatial.
+La inferencia de mapas está disponible mediante una importación explícita de
+wall2wall.prediction.
 
 ## Precondiciones
 Python 3.11 o posterior y el paquete accesible desde el intérprete consumidor.
 No requiere capas, campos, CRS ni archivos de datos para importar.
 
 ## Resultados
-Permite import wall2wall. No aplica generación de archivos al importar este
-módulo; la inferencia de mapas todavía no está implementada.
+Permite import wall2wall sin generar archivos al importar este módulo.
 
 ## Notas relevantes
 No importa motores opcionales, Snakemake ni dependencias científicas al cargar.
diff --git a/08_pkg/CONTEXT.md b/08_pkg/CONTEXT.md
index 5e40c40..c7a2f01 100644
--- a/08_pkg/CONTEXT.md
+++ b/08_pkg/CONTEXT.md
@@ -17,11 +17,15 @@ cuatro entregas M004-S01, M004-S02, M004-S03 y M004-S04 están aceptadas. La fá
 opcional wall2wall.engines.make_regressor está disponible; la cualificación real
 comprende LightGBM 4.6.0 y XGBoost 3.1.3 con Python 3.11.16 en el perfil Windows
 del proyecto. No implica soporte universal ni equivalencia entre plataformas.
-M005-S01 está aceptado: wall2wall.audit guarda y carga expedientes portables
-con confianza explícita, integridad y compatibilidad comprobadas. M005-S02 está
-aceptado: wall2wall.prediction.predict_raster produce GeoTIFF por ventanas desde
-un expediente confiable. Calidad y prueba de escala M005-S03, workflow de producción,
-Linux M001 y cualificación integral Windows M008 siguen pendientes.
+M005 está cerrado y M005-S00, M005-S01, M005-S02 y M005-S03 están aceptados.
+wall2wall.audit guarda y carga expedientes portables con confianza explícita,
+integridad y compatibilidad comprobadas. wall2wall.prediction.predict_raster
+produce mapas GeoTIFF por ventanas desde un expediente confiable. El modo
+`quality=True` añade validez y alerta univariada min/max; la escala está acreditada
+con el protocolo técnico 1024×1024×8 y 2048×2048×8 en Windows D014. Esta evidencia
+no acredita cualificación entre plataformas, AOA, incertidumbre ni utilidad
+predictiva. El workflow de producción M006, Linux M001 y la cualificación integral
+Windows M008 siguen pendientes.
 El registro autoritativo de evidencia y aceptación sigue siendo el ledger.
 Contratos en 00_brief/architecture.md y 00_brief/validation.md; alcance en roadmap.yaml.
 El pyproject y tests de la raíz pertenecen a la plantilla, no al producto.
```
