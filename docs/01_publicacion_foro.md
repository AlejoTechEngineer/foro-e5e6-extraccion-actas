# Publicación del foro (Escenarios 5 y 6)

**Grupo 11** — Publica: Alejandro de Mendoza Tovar.

## 1. Problema
Una entidad pública del orden nacional (nombre reservado por confidencialidad) debe validar 5.082 actas escaneadas
de un programa de apoyo a hogares, en tres tipos, sin capa de texto y con 29 a 35 variables por acta. Su prototipo de
extracción automática (OCR, expresiones regulares y reglas de validación) reporta una completitud del 85 %, pero esa
medida solo indica si el campo tiene valor, no si es correcto. En un piloto con siete actas, el número de acta se
extrajo en 0 % (0/7), el documento del funcionario en 42,9 % (3/7) y la fecha en 57,1 % (4/7). Por eso todas las actas
se validan a mano, con un ciclo de unas ocho semanas, y ninguna revisión deja registro (0 % trazables). Indicador:
tasa de extracción por campo crítico.

## 2. Antecedentes: las cuatro fuentes
**Académicas**
1. Paleyes, Urma y Lawrence (2022) revisaron informes de despliegue de aprendizaje automático en distintas industrias,
   ordenados por etapas del flujo, y encontraron dificultades en cada etapa. *Aporta:* la brecha no se atribuye solo al
   OCR; hay que medir el sistema completo contra actas validadas. DOI: https://doi.org/10.1145/3533378
2. Memon et al. (2020) sintetizaron 142 artículos sobre OCR manuscrito (2000 a 2018) y señalaron brechas de investigación.
   *Aporta:* el manuscrito exige técnicas propias; sus campos se evalúan aparte. DOI: https://doi.org/10.1109/ACCESS.2020.3012542

**Técnicas**
3. Tesseract OCR (s. f.), documentación del motor de la versión 1.0: rinde mejor con al menos 300 ppp, la inclinación
   deteriora la segmentación y, para regiones pequeñas, conviene otro modo de segmentación y listas de caracteres
   permitidos. *Aporta:* guía el preprocesamiento y la extracción por zonas de H1. https://tesseract-ocr.github.io/tessdoc/ImproveQuality
4. Filcik y Murphy (2026), caso de Microsoft con una aseguradora: confianza por campo calibrada con más de 22.000 valores
   de documentos reales verificados por personas; 41 % menos valores a revisión dirigida, que aún incluía más del 80 % de
   los errores conocidos. *Aporta:* sustenta H2. https://devblogs.microsoft.com/foundry/content-understanding-confidence-grounding-hitl/

## 3. Pregunta de investigación
¿Qué factores del documento, del método de extracción y de la forma de ejecución explican que el prototipo de extracción
automática no alcance la exactitud requerida en los campos críticos de las actas escaneadas?

## 4. Hipótesis sobre la implementación de la solución
**H1.** Preprocesar los escaneos (corrección de inclinación, binarización, 300 ppp) y extraer cada campo crítico por zona
con caracteres permitidos, en lugar de OCR genérico de página completa, eleva a al menos 90 % la exactitud del número de
acta, el documento del funcionario y la fecha, frente a la versión 1.0.
- VI: método de extracción · VD: exactitud por campo crítico frente a la transcripción manual.
- Evidencia: cuantitativa; muestra estratificada; ambas versiones sobre las mismas actas. Descarte: no supera la línea base o no llega a 90 %.

**H2.** Revisar a mano solo los campos en amarillo o rojo del semáforo, con umbrales calibrados por tipo de acta y campo,
reduce el tiempo de revisión por acta frente a la validación 100 % manual, sin que más del 2 % de los errores críticos
quede sin corregir (umbral propuesto, a acordar con la Entidad).
- VI: modo de validación · VD: tiempo por acta y errores críticos sin corregir.
- Evidencia: cuantitativa y cualitativa. Descarte: el tiempo no baja o el error supera el umbral.
