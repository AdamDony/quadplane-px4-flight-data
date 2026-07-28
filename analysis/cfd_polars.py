#!/usr/bin/env python3
"""Reduce the raw Fluent force data in ``cfd/polars/LiftDrag.xlsx`` to
finite-wing coefficients and write ``figures/cfd_polars.png``.

The simulated geometry (``cad/WingForSimu.STEP``) is an untwisted, extruded
S1223 panel: 11.5 in (0.292 m) chord x 40 in (1.016 m) span, planform area
0.297 m^2, aspect ratio 3.48. Forces are therefore normalized by the panel
area, giving finite-wing (not 2-D section) coefficients.

Reduced results (V = 15 m/s, rho = 1.225 kg/m^3, Re ~ 3.0e5):
    C_L: 0.31 (-5 deg) .. 1.23 (+15 deg), slope ~2.64/rad, alpha_0L ~ -12 deg
    drag polar fit: C_D0 = 0.018, k = 0.120  ->  Oswald e = 0.77
    max L/D ~ 10.4 near alpha = 0 deg

Usage:  python analysis/cfd_polars.py   (from the repo root)
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import openpyxl

REPO = Path(__file__).resolve().parent.parent

# panel geometry measured from cad/WingForSimu.STEP (inches -> metres)
CHORD = 11.5 * 0.0254
SPAN = 40.0 * 0.0254
S_PANEL = CHORD * SPAN
AR = SPAN**2 / S_PANEL
RHO, V_INF, MU = 1.225, 15.0, 1.789e-5
Q_INF = 0.5 * RHO * V_INF**2

SURFACE, INK, INK_2, MUTED, GRID, BASELINE = (
    "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7")
BLUE, ORANGE = "#2a78d6", "#eb6834"

plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE, "axes.edgecolor": BASELINE,
    "axes.labelcolor": INK_2, "axes.titlecolor": INK,
    "axes.titlesize": 11, "axes.titleweight": "bold", "axes.labelsize": 9.5,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.7,
    "xtick.color": MUTED, "ytick.color": MUTED,
    "xtick.labelsize": 8.5, "ytick.labelsize": 8.5,
    "axes.spines.top": False, "axes.spines.right": False,
    "font.family": "sans-serif", "legend.frameon": False,
    "legend.fontsize": 9,
})


def main() -> None:
    ws = openpyxl.load_workbook(
        REPO / "cfd/polars/LiftDrag.xlsx", data_only=True).active
    rows = [r for r in ws.iter_rows(min_row=2, values_only=True) if r[0] is not None]
    aoa = np.array([r[0] for r in rows], dtype=float)
    lift = np.array([r[1] for r in rows], dtype=float)
    drag = np.array([r[2] for r in rows], dtype=float)

    cl, cd = lift / (Q_INF * S_PANEL), drag / (Q_INF * S_PANEL)
    slope, icpt = np.polyfit(np.radians(aoa), cl, 1)
    k, cd0 = np.polyfit(cl**2, cd, 1)
    e = 1 / (np.pi * AR * k)

    print(f"panel: S = {S_PANEL:.3f} m^2, AR = {AR:.2f}, "
          f"Re = {RHO * V_INF * CHORD / MU:.3g}")
    print(f"C_La = {slope:.2f}/rad, alpha_0L = {-icpt / slope * 180 / np.pi:.1f} deg")
    print(f"C_D0 = {cd0:.4f}, k = {k:.3f}, Oswald e = {e:.2f}, "
          f"max L/D = {(cl / cd).max():.1f}")

    fig, axes = plt.subplots(1, 3, figsize=(11, 3.6), dpi=150)
    fig.subplots_adjust(wspace=0.35, bottom=0.17, left=0.06, right=0.985)

    ax = axes[0]
    aa = np.linspace(aoa.min() - 1, aoa.max() + 1, 50)
    ax.plot(aa, icpt + slope * np.radians(aa), color=BASELINE, lw=1.2,
            label=fr"fit: $C_{{L_\alpha}}$ = {slope:.2f}/rad")
    ax.plot(aoa, cl, "o", color=BLUE, ms=6, zorder=5, label="Fluent, 15 m/s")
    ax.set_title("Lift coefficient", loc="left")
    ax.set_xlabel(r"$\alpha$ [deg]"); ax.set_ylabel(r"$C_L$")
    ax.legend(loc="upper left")

    ax = axes[1]
    cdfit = cd0 + k * (icpt + slope * np.radians(aa)) ** 2
    ax.plot(aa, cdfit, color=BASELINE, lw=1.2, label="parabolic polar")
    ax.plot(aoa, cd, "o", color=BLUE, ms=6, zorder=5)
    ax.set_title("Drag coefficient", loc="left")
    ax.set_xlabel(r"$\alpha$ [deg]"); ax.set_ylabel(r"$C_D$")
    ax.legend(loc="upper left")

    ax = axes[2]
    cl2 = np.linspace(0, (cl**2).max() * 1.1, 20)
    ax.plot(cl2, cd0 + k * cl2, color=BASELINE, lw=1.2,
            label=fr"$C_{{D_0}}$ = {cd0:.3f},  $e$ = {e:.2f}")
    ax.plot(cl**2, cd, "o", color=BLUE, ms=6, zorder=5)
    ax.set_title("Induced-drag fit", loc="left")
    ax.set_xlabel(r"$C_L^{\,2}$"); ax.set_ylabel(r"$C_D$")
    ax.legend(loc="upper left")

    out = REPO / "figures" / "cfd_polars.png"
    fig.savefig(out, bbox_inches="tight")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
