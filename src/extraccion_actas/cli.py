"""Línea de comandos: `python -m extraccion_actas` regenera reports/dimensionamiento.json y las figuras."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from . import estadistica as E
from .figuras import fig_aceptacion, fig_muestra, fig_piloto


def calcular() -> dict:
    R: dict = {}
    R["piloto"] = {c: {"k": k, "n": 7, "p": k / 7, "ic": E.wilson(k, 7)}
                   for c, k in {"numero_acta": 0, "documento_funcionario": 3, "fecha": 4}.items()}
    R["piloto"]["promedio_tres_campos"] = {"k": 7, "n": 21, "p": 7 / 21, "ic": E.wilson(7, 21)}
    R["estimacion"] = []
    for m in (0.10, 0.075, 0.05, 0.03):
        a, b = E.n_estimacion(0.5, m), E.n_estimacion(0.9, m)
        R["estimacion"].append({"E": m, "p05_n0": a[0], "p05_fpc": a[1], "p09_n0": b[0], "p09_fpc": b[1]})
    R["aceptacion"] = {f"{p:.2f}": E.n_aceptacion(p) for p in (0.93, 0.95, 0.97, 0.98, 0.99)}
    R["lb_n150"] = {f"{p:.2f}": E.limite_inferior(p, 150) for p in (0.93, 0.95, 0.97, 0.98, 0.99)}
    R["mcnemar"] = []
    for base, nuevo, p10 in ((0.43, 0.90, 0.02), (0.43, 0.90, 0.05), (0.60, 0.90, 0.02),
                             (0.60, 0.90, 0.05), (0.75, 0.90, 0.02), (0.75, 0.90, 0.05)):
        p01 = (nuevo - base) + p10
        R["mcnemar"].append({"base": base, "nuevo": nuevo, "p10": p10, "p01": round(p01, 3), "n": E.n_mcnemar(p01, p10)})
    R["tiempo_pareado"] = {str(d): E.n_tiempo_pareado(d) for d in (0.3, 0.5, 0.8, 1.0)}
    R["error_residual"] = {f"{t:.3f}": E.n_error_residual(t) for t in (0.0, 0.005, 0.01)}
    R["esfuerzo"] = {"horas_ciclo": 5 * 40 * 8, "min_por_acta": E.min_por_acta()}
    R["escenarios_esfuerzo"] = [{"f": f, "a": a, "carga": E.carga_relativa(f, a), "reduccion": 1 - E.carga_relativa(f, a),
                                 "semanas": 8 * E.carga_relativa(f, a)} for f in (0.3, 0.5, 0.7, 0.9) for a in (0.05, 0.10, 0.20)]
    R["referencia"] = {"actas": 450, "fraccion_universo": 450 / E.N_TOTAL, "horas_doble_transcripcion": 450 * 2 * 6 / 60,
                       "semanas_1_persona_40h": 450 * 2 * 6 / 60 / 40}
    R["campos_referencia"] = 450 * 3
    return R


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(prog="extraccion-actas", description=__doc__)
    ap.add_argument("--salida", type=Path, default=Path("reports"))
    a = ap.parse_args(argv)
    (a.salida / "figures").mkdir(parents=True, exist_ok=True)
    R = calcular()
    (a.salida / "dimensionamiento.json").write_text(json.dumps(R, indent=1, ensure_ascii=False), encoding="utf-8")
    fig_piloto(a.salida / "figures" / "f4_piloto.png")
    fig_muestra(a.salida / "figures" / "f5_muestra.png")
    fig_aceptacion(a.salida / "figures" / "f6_aceptacion.png")
    print(f"OK. Resultados en {a.salida}/dimensionamiento.json")


if __name__ == "__main__":
    main()
