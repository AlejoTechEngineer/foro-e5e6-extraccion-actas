"""Figuras del dimensionamiento (intervalos del piloto, tamaño de muestra, criterio de aceptación)."""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from .estadistica import N_TIPO, Z, wilson

TEAL, NAVY, VERDE, ROJO, AMA = "#1E98BE", "#0F385A", "#2E8B57", "#B3261E", "#E0A800"


def fig_piloto(ruta: Path) -> None:
    campos = [("N.º de acta (0/7)", 0, 7), ("Documento del\nfuncionario (3/7)", 3, 7),
              ("Fecha (4/7)", 4, 7), ("Promedio de los tres\ncampos (7/21)", 7, 21)]
    fig, ax = plt.subplots(figsize=(8, 3.6))
    for i, (lab, k, n) in enumerate(campos):
        lo, hi = wilson(k, n); y = len(campos) - i
        ax.plot([lo * 100, hi * 100], [y, y], color=TEAL, lw=5, solid_capstyle="butt")
        ax.plot(k / n * 100, y, "o", color=NAVY, ms=7)
        ax.text(hi * 100 + 1.5, y, f"{k / n * 100:.1f} % [{lo * 100:.1f}; {hi * 100:.1f}]", va="center", fontsize=8)
    ax.axvline(90, color=VERDE, ls="--", lw=1.3)
    ax.set_yticks(range(len(campos), 0, -1)); ax.set_yticklabels([c[0] for c in campos], fontsize=8.5)
    ax.set_xlim(0, 112); ax.set_xlabel("Tasa de extracción (%) e IC de Wilson al 95 %", fontsize=8.5)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(); fig.savefig(ruta, dpi=170); plt.close(fig)


def fig_muestra(ruta: Path) -> None:
    e = np.linspace(0.03, 0.12, 100)
    fig, ax = plt.subplots(figsize=(7.5, 3.8))
    for p, c, lab in ((0.5, NAVY, "Sin información previa (p = 0,5)"), (0.9, TEAL, "Exactitud esperada 90 % (p = 0,9)")):
        n0 = Z ** 2 * p * (1 - p) / e ** 2
        ax.plot(e * 100, n0 / (1 + (n0 - 1) / N_TIPO), color=c, lw=2, label=lab)
    ax.axhline(150, color=ROJO, ls="--", lw=1.2)
    ax.set_xlabel("Margen de error (± puntos porcentuales)", fontsize=8.5); ax.set_ylabel("Actas por tipo", fontsize=8.5)
    ax.legend(fontsize=8, frameon=False); ax.spines[["top", "right"]].set_visible(False); ax.invert_xaxis()
    fig.tight_layout(); fig.savefig(ruta, dpi=170); plt.close(fig)


def fig_aceptacion(ruta: Path) -> None:
    ns = np.arange(20, 401)
    fig, ax = plt.subplots(figsize=(7.5, 3.8))
    for ph, c in ((0.93, ROJO), (0.95, AMA), (0.97, TEAL), (0.98, VERDE)):
        ax.plot(ns, [wilson(ph * n, n)[0] * 100 for n in ns], color=c, lw=2, label=f"exactitud observada {ph * 100:.0f} %")
    ax.axhline(90, color=NAVY, ls="--", lw=1.2); ax.axvline(150, color="gray", ls=":", lw=1.2)
    ax.set_ylim(78, 100); ax.set_xlabel("Actas evaluadas por tipo y campo", fontsize=8.5)
    ax.set_ylabel("Límite inferior del IC 95 % (%)", fontsize=8.5)
    ax.legend(fontsize=8, frameon=False, loc="lower right"); ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(); fig.savefig(ruta, dpi=170); plt.close(fig)
