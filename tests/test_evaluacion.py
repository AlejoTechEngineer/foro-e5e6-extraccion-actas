import numpy as np
import pandas as pd
import pytest

from extraccion_actas import evaluacion as V


def _registro(n, acierta_base, acierta_nueva, campo="n_acta", tipo="acompanamiento"):
    """Datos sintéticos construidos EN LA PRUEBA para verificar la lógica; no son datos del caso."""
    filas = []
    for i in range(n):
        ref = f"{1000 + i}"
        for ver, ok in (("v1.0", i < acierta_base), ("nueva", i < acierta_nueva)):
            filas.append({"id_acta": f"A{i}", "tipo_acta": tipo, "campo": campo, "version": ver,
                          "valor_extraido": ref if ok else "xx", "confianza": 0.9 if ok else 0.4,
                          "semaforo": "verde" if ok else "rojo", "valor_referencia": ref})
    return pd.DataFrame(filas)


def test_exactitud_vacio_no_cuenta():
    df = pd.DataFrame([{"id_acta": "A", "tipo_acta": "t", "campo": "c", "version": "v", "valor_extraido": "",
                        "confianza": 0.1, "semaforo": "rojo", "valor_referencia": "123"}])
    assert V.con_exactitud(df)["exacto"].iloc[0] == 0


def test_faltan_columnas():
    with pytest.raises(ValueError):
        V.con_exactitud(pd.DataFrame({"x": [1]}))


def test_exactitud_por_grupo_calcula_ic():
    ex = V.exactitud_por_grupo(V.con_exactitud(_registro(150, 60, 145)))
    nueva = ex[ex.version == "nueva"].iloc[0]
    assert nueva["n"] == 150 and nueva["exactos"] == 145
    assert nueva["ic95_inf"] < nueva["exactitud"] < nueva["ic95_sup"]


def test_mcnemar_cuenta_pares_discordantes():
    m = V.mcnemar_pareado(_registro(150, 60, 145), "v1.0", "nueva")
    assert m["empeoran"] == 0 and m["mejoran"] == 85 and m["p_mcnemar"] < 0.001


def test_h1_sostenida_con_muestra_suficiente():
    d = V.decision_h1(_registro(150, 60, 145), "v1.0", "nueva")   # 96,7 % observado
    assert d["decision"].iloc[0] == "SOSTENIDA"


def test_h1_parcial_cuando_el_limite_inferior_no_alcanza():
    d = V.decision_h1(_registro(150, 60, 140), "v1.0", "nueva")   # 93,3 %: LB < 90 %
    assert d["decision"].iloc[0].startswith("PARCIAL")


def test_h1_descartada_si_no_mejora():
    d = V.decision_h1(_registro(150, 140, 100), "v1.0", "nueva")
    assert d["decision"].iloc[0] == "DESCARTADA"


def test_h2_sostenida():
    rng = np.random.default_rng(1)
    manual = rng.normal(19, 3, 40)
    asistido = manual - rng.normal(8, 2, 40)
    r = V.decision_h2(manual, asistido, errores=2, campos=1350)
    assert r["decision"] == "SOSTENIDA" and r["error_ic95"][1] <= 0.02


def test_h2_descartada_si_el_error_supera_el_techo():
    manual = np.arange(20, 60, dtype=float); asistido = manual - 5
    assert V.decision_h2(manual, asistido, errores=40, campos=1350)["decision"] == "DESCARTADA"


def test_h2_exige_pares_suficientes():
    with pytest.raises(ValueError):
        V.decision_h2([1, 2, 3], [1, 2, 3], 0, 100)


def test_calibrar_umbral_cubre_los_errores():
    conf = pd.Series([0.2, 0.3, 0.4, 0.95, 0.96, 0.97, 0.98, 0.99, 0.99, 0.99])
    exa = pd.Series([0, 0, 0, 1, 1, 1, 1, 1, 1, 0])        # 4 errores; uno con confianza alta
    r = V.calibrar_umbral(conf, exa, cobertura=0.75)
    assert r is not None and r["cobertura"] >= 0.75 and r["carga"] <= 0.5


def test_calibrar_umbral_sin_poder_de_separacion_exige_revisar_todo():
    """Si la confianza no separa errores de aciertos, la carga de revisión necesaria es 100 %."""
    conf = pd.Series([0.9] * 10)
    exa = pd.Series([0, 1] * 5)
    r = V.calibrar_umbral(conf, exa, cobertura=0.8)
    assert r["carga"] == 1.0
