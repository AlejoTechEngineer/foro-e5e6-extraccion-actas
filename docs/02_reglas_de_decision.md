# Reglas de decisión (fijadas antes de ver los datos)

| Hipótesis | Se sostiene | Parcial | Se descarta |
|---|---|---|---|
| **H1** (por tipo de acta y campo) | Límite inferior del IC de Wilson ≥ 90 % **y** mejora frente a la v1.0 (McNemar exacto, p < 0,05) | Estimación puntual ≥ 90 % pero límite inferior < 90 %: **ampliar la muestra, no concluir** | No supera a la v1.0 o la estimación puntual < 90 % |
| **H2** | Mediana del tiempo por acta baja (Wilcoxon pareado, p < 0,05) **y** límite superior del error crítico sin corregir ≤ 2 % | — | El tiempo no baja o el límite superior > 2 % |
| **D1** | La exactitud de la v1.0 es menor en manuscritos que en impresos/numéricos | — | No hay diferencia |
| **D2** | La exactitud de la v1.0 baja con menor resolución o mayor inclinación | — | Sin relación |

Implementación: `extraccion_actas.evaluacion.decision_h1` y `decision_h2`. El umbral de 90 % proviene del semáforo
actual; el de 2 % es una **propuesta** que debe acordarse con la Entidad.
