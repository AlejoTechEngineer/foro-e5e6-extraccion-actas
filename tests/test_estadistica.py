import pytest

from extraccion_actas import estadistica as E


def test_wilson_piloto_numero_de_acta():
    lo, hi = E.wilson(0, 7)
    assert lo == pytest.approx(0.0, abs=1e-9) and hi == pytest.approx(0.354, abs=0.001)


def test_wilson_documento_y_fecha():
    assert E.wilson(3, 7)[0] == pytest.approx(0.158, abs=0.001)
    assert E.wilson(4, 7)[1] == pytest.approx(0.842, abs=0.001)


def test_promedio_tres_campos_del_piloto():
    assert 7 / 21 == pytest.approx(0.3333, abs=1e-4)


@pytest.mark.parametrize("p,esperado", [(0.93, 385), (0.95, 139), (0.97, 71), (0.98, 55), (0.99, 43)])
def test_n_aceptacion(p, esperado):
    assert E.n_aceptacion(p) == esperado


def test_diseno_150_acepta_95_pero_no_93():
    assert E.limite_inferior(0.95, 150) >= 0.90
    assert E.limite_inferior(0.93, 150) < 0.90


def test_n_estimacion_con_correccion_menor_que_sin_ella():
    n0, nfpc = E.n_estimacion(0.5, 0.05)
    assert n0 == 385 and nfpc == 314 and nfpc < n0


def test_n_mcnemar_escenario_piloto():
    assert E.n_mcnemar(0.49, 0.02) == 16


def test_n_mcnemar_crece_cuando_la_mejora_es_menor():
    assert E.n_mcnemar(0.17, 0.02) > E.n_mcnemar(0.32, 0.02) > E.n_mcnemar(0.49, 0.02)


def test_n_tiempo_pareado():
    assert E.n_tiempo_pareado(0.5) == 34 and E.n_tiempo_pareado(0.8) == 15


def test_n_error_residual():
    assert E.n_error_residual(0.005) == 335 and E.n_error_residual(0.0) == 189


def test_esfuerzo_supuesto_y_carga():
    assert E.min_por_acta() == pytest.approx(18.89, abs=0.01)
    assert E.carga_relativa(0.5, 0.10) == pytest.approx(0.55)
