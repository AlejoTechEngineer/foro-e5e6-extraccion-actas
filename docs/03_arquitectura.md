# Arquitectura de referencia

```mermaid
flowchart LR
  A[Actas PDF por tipo] --> B[Preprocesamiento de imagen]
  B --> C[Clasificador de tipo y zonas]
  C --> D[Extracción por tipo - Strategy]
  D --> E[Reglas de validación cruzada]
  E --> F{Semáforo por campo}
  F -- verde --> G[Aceptar + muestra de auditoría]
  F -- amarillo/rojo --> H[Cola de revisión humana]
  G --> I[(Registro de trazabilidad)]
  H --> I
  R[Conjunto de referencia 450 actas] --> V[Evaluación de exactitud]
  V --> K[Calibración de umbrales]
  K --> F
```

## Decisiones (ADR)
| ADR | Decisión | Justificación |
|---|---|---|
| 001 | Arquitectura por capas con patrón Strategy por tipo de acta | Tres formatos con variables propias |
| 002 | Evaluar contra un conjunto de referencia antes de operar | Ninguna versión se ha evaluado contra actas validadas; completitud ≠ exactitud |
| 003 | Semáforo **por campo** con umbrales calibrados y versionados | Un semáforo por acta oculta errores en campos críticos |
| 004 | Registro de trazabilidad de solo adición | Hoy 0 % de validaciones trazables |
| 005 | Procesar dentro de la infraestructura de la Entidad | Datos personales (Ley 1581 de 2012) |

Más detalle y figuras: `reports/figures/f1_arbol.png`, `f2_arquitectura.png`, `f3_flujo.png`.
