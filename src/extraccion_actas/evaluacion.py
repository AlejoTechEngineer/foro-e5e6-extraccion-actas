"""Herramientas para evaluar la extracción contra el conjunto de referencia (H1, H2, D1, D2).

Esquema del registro de evaluación (una fila por campo de un acta): ver data/plantillas/diccionario.md.
Este módulo NO incluye datos: trabaja con los que la Entidad produzca dentro de su infraestructura.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats

from .estadistica import wilson

COLUMNAS = ["id_acta", "tipo_acta", "campo", "version", "valor_extraido", "confianza",
            "semaforo", "valor_referencia"]


def normalizar(s: pd.Series) -> pd.Series:
    """Normalización mínima para comparar valores: texto sin espacios sobrantes. Vacío => no exacto."""
    return s.astype("string").str.strip()


def con_exactitud(df: pd.DataFrame) -> pd.DataFrame:
    """Agrega la columna 'exacto' (1 si el valor extraído es idéntico al de referencia; vacío no cuenta)."""
    faltan = [c for c in COLUMNAS if c not in df.columns]
    if faltan:
        raise ValueError(f"Faltan columnas: {faltan}")
    d = df.copy()
    ext, ref = normalizar(d["valor_extraido"]), normalizar(d["valor_referencia"])
    d["exacto"] = ((ext == ref) & ext.notna() & (ext != "")).astype(int)
    return d


def exactitud_por_grupo(df: pd.DataFrame) -> pd.DataFrame:
    """Exactitud por versión, tipo de acta y campo, con intervalo de Wilson al 95 %."""
    d = df if "exacto" in df.columns else con_exactitud(df)
    filas = []
    for (ver, tipo, campo), g in d.groupby(["version", "tipo_acta", "campo"]):
        k, n = int(g["exacto"].sum()), len(g)
        lo, hi = wilson(k, n)
        filas.append({"version": ver, "tipo_acta": tipo, "campo": campo, "n": n, "exactos": k,
                      "exactitud": k / n, "ic95_inf": lo, "ic95_sup": hi})
    return pd.DataFrame(filas)


def mcnemar_pareado(df: pd.DataFrame, base: str, nueva: str) -> dict:
    """Prueba exacta de McNemar: la versión base y la nueva se ejecutan sobre las MISMAS actas y campos."""
    d = df if "exacto" in df.columns else con_exactitud(df)
    p = d.pivot_table(index=["id_acta", "campo"], columns="version", values="exacto", aggfunc="first")
    p = p[[base, nueva]].dropna()
    b = int(((p[base] == 1) & (p[nueva] == 0)).sum())   # empeoran
    c = int(((p[base] == 0) & (p[nueva] == 1)).sum())   # mejoran
    n = b + c
    pval = 1.0 if n == 0 else min(1.0, 2 * float(stats.binomtest(min(b, c), n, 0.5).pvalue))
    return {"pares": len(p), "empeoran": b, "mejoran": c, "p_mcnemar": pval}


def decision_h1(df: pd.DataFrame, base: str, nueva: str, meta: float = 0.90) -> pd.DataFrame:
    """Regla de decisión de H1 (fijada antes de ver los datos), por tipo de acta y campo.

    SOSTENIDA: límite inferior de Wilson >= meta y mejora frente a la base (McNemar p < 0,05).
    PARCIAL: estimación puntual >= meta pero límite inferior < meta (ampliar la muestra, no concluir).
    DESCARTADA: no supera a la base o la estimación puntual no alcanza la meta.
    """
    d = con_exactitud(df)
    ex = exactitud_por_grupo(d)
    filas = []
    for (tipo, campo), g in d.groupby(["tipo_acta", "campo"]):
        m = mcnemar_pareado(g, base, nueva)
        fila = ex[(ex.version == nueva) & (ex.tipo_acta == tipo) & (ex.campo == campo)].iloc[0]
        base_p = ex[(ex.version == base) & (ex.tipo_acta == tipo) & (ex.campo == campo)]["exactitud"].iloc[0]
        mejora = fila["exactitud"] > base_p and m["p_mcnemar"] < 0.05
        if mejora and fila["ic95_inf"] >= meta:
            dec = "SOSTENIDA"
        elif fila["exactitud"] >= meta and fila["exactitud"] > base_p:
            dec = "PARCIAL (ampliar la muestra)"
        else:
            dec = "DESCARTADA"
        filas.append({"tipo_acta": tipo, "campo": campo, "exactitud_base": base_p,
                      "exactitud_nueva": fila["exactitud"], "ic95_inf": fila["ic95_inf"],
                      "p_mcnemar": m["p_mcnemar"], "decision": dec})
    return pd.DataFrame(filas)


def decision_h2(t_manual, t_asistido, errores: int, campos: int, techo: float = 0.02) -> dict:
    """Regla de decisión de H2: el tiempo mediano baja (Wilcoxon pareado) y el límite SUPERIOR del
    error crítico sin corregir es <= techo."""
    tm, ta = np.asarray(t_manual, float), np.asarray(t_asistido, float)
    if len(tm) != len(ta) or len(tm) < 6:
        raise ValueError("Se requieren al menos 6 pares de tiempos de las mismas actas")
    dif = tm - ta
    p_w = float(stats.wilcoxon(dif, alternative="greater").pvalue) if np.any(dif != 0) else 1.0
    lo, hi = wilson(errores, campos)
    baja = float(np.median(dif)) > 0 and p_w < 0.05
    dec = "SOSTENIDA" if baja and hi <= techo else "DESCARTADA"
    return {"mediana_reduccion_min": float(np.median(dif)), "p_wilcoxon": p_w,
            "error_ic95": (lo, hi), "decision": dec}


def calibrar_umbral(conf: pd.Series, exacto: pd.Series, cobertura: float = 0.80) -> dict:
    """Umbral de confianza que envía a revisión (confianza < umbral) al menos `cobertura` de los errores
    con la menor carga de revisión. Si la confianza no separa errores de aciertos, la carga resultante es
    1,0 (hay que revisar todo y el campo no se automatiza). Debe validarse luego en actas que NO se usaron
    para calibrar."""
    c, e = pd.Series(conf).astype(float).reset_index(drop=True), pd.Series(exacto).astype(int).reset_index(drop=True)
    errores = int((e == 0).sum())
    if errores == 0:
        return {"umbral": float(c.min()), "cobertura": 1.0, "carga": 0.0}
    mejor = None
    for t in sorted(c.unique()) + [float(c.max()) + 1e-9]:
        marcado = c < t
        cob = float(((e == 0) & marcado).sum() / errores)
        carga = float(marcado.mean())
        if cob >= cobertura and (mejor is None or carga < mejor["carga"]):
            mejor = {"umbral": float(t), "cobertura": cob, "carga": carga}
    return mejor
