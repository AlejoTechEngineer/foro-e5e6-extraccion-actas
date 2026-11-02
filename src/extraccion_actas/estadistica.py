"""Dimensionamiento estadístico del estudio (sección 8 del documento).

Todo parte de cifras del caso (piloto de 7 actas; 1.694 actas por tipo; 5.082 en total) y de supuestos
rotulados. No procesa actas ni contiene datos personales.
"""
from __future__ import annotations

import math

from scipy import stats
from statsmodels.stats.power import TTestPower
from statsmodels.stats.proportion import proportion_confint

N_TIPO = 1694   # actas por tipo (caso)
N_TOTAL = 5082  # actas totales (caso)
Z = float(stats.norm.ppf(0.975))


def wilson(k: float, n: int, alfa: float = 0.05) -> tuple[float, float]:
    """Intervalo de confianza de Wilson para una proporción k/n."""
    lo, hi = proportion_confint(k, n, alpha=alfa, method="wilson")
    return max(float(lo), 0.0), float(hi)


def n_estimacion(p: float, margen: float, poblacion: int = N_TIPO) -> tuple[int, int]:
    """Actas para estimar una proporción con un margen de error (sin y con corrección por población finita)."""
    n0 = Z ** 2 * p * (1 - p) / margen ** 2
    return math.ceil(n0), math.ceil(n0 / (1 + (n0 - 1) / poblacion))


def limite_inferior(p_obs: float, n: int) -> float:
    """Límite inferior del IC de Wilson si la exactitud observada es p_obs con n evaluaciones."""
    return wilson(p_obs * n, n)[0]


def n_aceptacion(p_obs: float, meta: float = 0.90) -> int:
    """Menor n para el que el límite inferior de Wilson de una exactitud observada p_obs alcanza la meta."""
    for n in range(10, 20000):
        if limite_inferior(p_obs, n) >= meta:
            return n
    raise ValueError("No se alcanza la meta con n < 20000")


def n_mcnemar(p01: float, p10: float, alfa: float = 0.05, potencia: float = 0.80) -> int:
    """Pares necesarios para McNemar (aproximación de Connor, 1987)."""
    psi, d = p01 + p10, p01 - p10
    za, zb = stats.norm.ppf(1 - alfa / 2), stats.norm.ppf(potencia)
    return math.ceil((za * math.sqrt(psi) + zb * math.sqrt(psi - d ** 2)) ** 2 / d ** 2)


def n_tiempo_pareado(d: float, alfa: float = 0.05, potencia: float = 0.80) -> int:
    """Pares necesarios para una prueba t pareada con tamaño del efecto d de Cohen."""
    return math.ceil(TTestPower().solve_power(effect_size=d, alpha=alfa, power=potencia,
                                              alternative="two-sided"))


def n_error_residual(tasa: float, techo: float = 0.02) -> int:
    """Campos necesarios para que el límite SUPERIOR de Wilson de una tasa de error sea <= techo."""
    for n in range(20, 50000):
        if wilson(tasa * n, n)[1] <= techo:
            return n
    raise ValueError("No se alcanza el techo con n < 50000")


def min_por_acta(personas: int = 5, horas_semana: float = 40, semanas: float = 8,
                 actas: int = N_TOTAL) -> float:
    """SUPUESTO: dedicación completa del equipo durante el ciclo => minutos promedio por acta."""
    return personas * horas_semana * semanas * 60 / actas


def carga_relativa(f: float, a: float) -> float:
    """Carga relativa de revisión: fracción f de campos enviados a revisión más auditoría a de los verdes."""
    return f + a * (1 - f)
