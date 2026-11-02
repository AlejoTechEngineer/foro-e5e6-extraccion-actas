import json

from extraccion_actas.cli import calcular, main


def test_calcular_reproduce_las_cifras_del_documento():
    R = calcular()
    assert R["aceptacion"]["0.95"] == 139 and R["tiempo_pareado"]["0.5"] == 34
    assert R["mcnemar"][0]["n"] == 16 and R["campos_referencia"] == 1350
    assert round(R["esfuerzo"]["min_por_acta"]) == 19


def test_main_escribe_json_y_figuras(tmp_path):
    main(["--salida", str(tmp_path)])
    assert json.loads((tmp_path / "dimensionamiento.json").read_text(encoding="utf-8"))["aceptacion"]
    for f in ("f4_piloto.png", "f5_muestra.png", "f6_aceptacion.png"):
        assert (tmp_path / "figures" / f).exists()
