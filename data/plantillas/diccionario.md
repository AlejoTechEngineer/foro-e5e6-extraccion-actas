# Diccionario del registro de evaluación

Una fila por **campo de un acta**. **No se versionan datos reales**: el archivo se diligencia dentro de la
infraestructura de la Entidad (Ley 1581 de 2012) y `data/reales/` está en `.gitignore`.

| Campo | Tipo | Descripción |
|---|---|---|
| `id_acta` | texto | Identificador **seudonimizado** del acta |
| `tipo_acta` | categórico | `acompanamiento` / `entrega_insumos` / `vinculacion` |
| `campo` | categórico | Campo crítico evaluado (mínimo: `n_acta`, `documento_funcionario`, `fecha`) |
| `version` | categórico | Versión del prototipo (`v1.0`, `v2.0`, `v3.0`, `nueva`) |
| `valor_extraido` | texto | Valor que produjo el prototipo (vacío si no extrajo nada) |
| `confianza` | real 0–1 | Confianza reportada para ese valor |
| `semaforo` | categórico | `verde` / `amarillo` / `rojo` asignado al campo |
| `valor_referencia` | texto | Transcripción de referencia (doble transcripción + adjudicación) |
| `resolucion_ppp`, `inclinacion_grados` | real | Metadatos de la imagen (hipótesis D2) |

`exacto` se calcula con `extraccion_actas.evaluacion.con_exactitud`: 1 si el valor extraído es idéntico al de
referencia (sin espacios sobrantes); un valor vacío **no** cuenta como exacto.
