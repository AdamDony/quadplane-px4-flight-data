#!/usr/bin/env python3
"""Generate flight-report figures from the PX4 telemetry CSVs.

Reads the per-topic CSV exports in ``data/telemetry/`` and writes PNG
figures to ``figures/``:

    flight_overview.png   altitude, speed, battery voltage, electrical power
    trajectory_3d.png     3-D flight path coloured by ground speed
    ground_track.png      top-down ground track coloured by altitude
    transition.png        attitude and lift-motor commands through the
                          hover -> forward-flight transition

Time base
---------
The sdlog2 CSV exports do not carry a per-row timestamp column. ``GPS.csv``
does carry ``GPS_GPSTime`` (microseconds), which bounds the session at
~24.02 min. Each topic is logged at a fixed rate while sdlog2 is running,
so every topic is assigned a uniform time axis spanning the GPS-derived
session length. This is accurate to within the logger's scheduling jitter
and is used for visualisation only - not for rate-sensitive analysis.

Usage
-----
    pip install -r analysis/requirements.txt
    python analysis/plot_flight.py            # from the repo root
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.collections import LineCollection
from matplotlib.colors import LinearSegmentedColormap

REPO = Path(__file__).resolve().parent.parent
TELEM = REPO / "data" / "telemetry"

# -- palette ---------------------------------------------------------------
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
BASELINE = "#c3c2b7"
BLUE, ORANGE, AQUA, YELLOW = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
# sequential blue ramp, light -> dark (magnitude encoding)
SEQ_BLUES = LinearSegmentedColormap.from_list(
    "seq_blue",
    ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"],
)

plt.rcParams.update(
    {
        "figure.facecolor": SURFACE,
        "axes.facecolor": SURFACE,
        "savefig.facecolor": SURFACE,
        "axes.edgecolor": BASELINE,
        "axes.labelcolor": INK_2,
        "axes.titlecolor": INK,
        "axes.titlesize": 11,
        "axes.titleweight": "bold",
        "axes.labelsize": 9.5,
        "axes.grid": True,
        "grid.color": GRID,
        "grid.linewidth": 0.7,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "xtick.labelsize": 8.5,
        "ytick.labelsize": 8.5,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "font.family": "sans-serif",
        "legend.frameon": False,
        "legend.fontsize": 9,
    }
)


def session_minutes() -> float:
    """Session length in minutes from the GPS microsecond clock."""
    t = pd.read_csv(TELEM / "GPS.csv", usecols=["GPS_GPSTime"])["GPS_GPSTime"]
    return float(t.iloc[-1] - t.iloc[0]) / 60e6


def load(topic: str, span_min: float) -> pd.DataFrame:
    """Load one topic CSV and attach a uniform time axis ``t`` (minutes)."""
    df = pd.read_csv(TELEM / f"{topic}.csv")
    df["t"] = np.linspace(0.0, span_min, len(df))
    return df


def flight_window(gpos: pd.DataFrame, pad_min: float = 0.5) -> tuple[float, float]:
    """[start, end] minutes of the actual flight (motion or altitude gain)."""
    vh = np.hypot(gpos.GPOS_VelN, gpos.GPOS_VelE)
    alt0 = gpos.GPOS_Alt.iloc[:50].median()
    active = (vh > 1.0) | (gpos.GPOS_Alt - alt0 > 3.0)
    t_active = gpos.t[active.to_numpy()]
    return max(0.0, t_active.iloc[0] - pad_min), min(
        gpos.t.iloc[-1], t_active.iloc[-1] + pad_min
    )


def crop(df: pd.DataFrame, win: tuple[float, float]) -> pd.DataFrame:
    return df[(df.t >= win[0]) & (df.t <= win[1])]


def speed_colored_path(ax, x, y, c, cmap=SEQ_BLUES, lw=2.0):
    """Draw a 2-D path as a line coloured by a scalar."""
    pts = np.column_stack([x, y]).reshape(-1, 1, 2)
    segs = np.concatenate([pts[:-1], pts[1:]], axis=1)
    lc = LineCollection(segs, cmap=cmap, linewidths=lw, capstyle="round")
    lc.set_array(np.asarray(c)[:-1])
    ax.add_collection(lc)
    ax.autoscale()
    return lc


# -- figures ---------------------------------------------------------------


def fig_overview(span, win, outdir):
    gpos = crop(load("GPOS", span), win)
    airs = crop(load("AIRS", span), win)
    batt = crop(load("BATT", span), win)

    fig, axes = plt.subplots(2, 2, figsize=(11, 6.4), dpi=150)
    fig.subplots_adjust(hspace=0.5, wspace=0.28, top=0.86, bottom=0.09)
    fig.suptitle(
        "Quadplane VTOL flight overview - 4 Sep 2022, Dhaka",
        fontsize=13, fontweight="bold", color=INK, x=0.07, ha="left",
    )

    ax = axes[0, 0]
    ax.plot(gpos.t, gpos.GPOS_Alt, color=BLUE, lw=1.8)
    ax.set_title("Altitude (AMSL)", loc="left")
    ax.set_ylabel("m")

    ax = axes[0, 1]
    vh = np.hypot(gpos.GPOS_VelN, gpos.GPOS_VelE)
    ax.plot(gpos.t, vh, color=BLUE, lw=1.8, label="ground speed (GPS)")
    ax.plot(airs.t, airs.AIRS_IndSpeed, color=ORANGE, lw=1.8, label="indicated airspeed")
    ax.set_title("Speed", loc="left")
    ax.set_ylabel("m/s")
    ax.legend(loc="lower center", ncol=2)

    ax = axes[1, 0]
    ax.plot(batt.t, batt.BATT_VFilt, color=BLUE, lw=1.8)
    ax.set_title("Battery voltage (6S pack)", loc="left")
    ax.set_ylabel("V")
    ax.set_xlabel("session time [min]")

    ax = axes[1, 1]
    power = batt.BATT_VFilt * batt.BATT_CFilt
    ax.plot(batt.t, power, color=BLUE, lw=1.8)
    ax.set_title("Electrical power draw", loc="left")
    ax.set_ylabel("W")
    ax.set_xlabel("session time [min]")

    fig.savefig(outdir / "flight_overview.png", bbox_inches="tight")
    plt.close(fig)


def fig_trajectory_3d(span, win, outdir):
    lpos = crop(load("LPOS", span), win)
    x, y = lpos.LPOS_Y.to_numpy(), lpos.LPOS_X.to_numpy()  # East, North
    z = -lpos.LPOS_Z.to_numpy()  # NED -> altitude AGL
    v = np.hypot(lpos.LPOS_VX, lpos.LPOS_VY).to_numpy()

    fig = plt.figure(figsize=(10, 7.2), dpi=150)
    ax = fig.add_subplot(projection="3d")
    ax.set_facecolor(SURFACE)
    pts = np.column_stack([x, y, z])
    from mpl_toolkits.mplot3d.art3d import Line3DCollection

    segs = np.stack([pts[:-1], pts[1:]], axis=1)
    lc = Line3DCollection(segs, cmap=SEQ_BLUES, linewidths=1.8)
    lc.set_array(v[:-1])
    ax.add_collection3d(lc)
    # ground-track shadow
    ax.plot(x, y, np.zeros_like(z), color=GRID, lw=1.0, zorder=0)
    ax.set_xlim(x.min(), x.max())
    ax.set_ylim(y.min(), y.max())
    ax.set_zlim(0, z.max() * 1.05)
    ax.set_xlabel("East [m]", color=INK_2)
    ax.set_ylabel("North [m]", color=INK_2)
    ax.set_zlabel("Altitude AGL [m]", color=INK_2)
    ax.tick_params(colors=MUTED, labelsize=8)
    ax.xaxis.pane.set_facecolor(SURFACE)
    ax.yaxis.pane.set_facecolor(SURFACE)
    ax.zaxis.pane.set_facecolor(SURFACE)
    ax.xaxis.pane.set_edgecolor(GRID)
    ax.yaxis.pane.set_edgecolor(GRID)
    ax.zaxis.pane.set_edgecolor(GRID)
    ax.view_init(elev=24, azim=-60)
    ax.set_title(
        "Flight path - local NED estimator (LPOS)",
        color=INK, fontweight="bold", fontsize=12,
    )
    cb = fig.colorbar(lc, ax=ax, shrink=0.55, pad=0.08)
    cb.set_label("ground speed [m/s]", color=INK_2, fontsize=9)
    cb.ax.tick_params(colors=MUTED, labelsize=8)
    cb.outline.set_edgecolor(BASELINE)
    fig.savefig(outdir / "trajectory_3d.png", bbox_inches="tight")
    plt.close(fig)


def fig_ground_track(span, win, outdir):
    lpos = crop(load("LPOS", span), win)
    x, y = lpos.LPOS_Y.to_numpy(), lpos.LPOS_X.to_numpy()
    alt = -lpos.LPOS_Z.to_numpy()

    fig, ax = plt.subplots(figsize=(9, 6.2), dpi=150)
    lc = speed_colored_path(ax, x, y, alt)
    ax.plot(x[0], y[0], "o", ms=8, color=AQUA, mec=SURFACE, mew=1.5, zorder=5)
    ax.annotate("launch", (x[0], y[0]), xytext=(-12, 14), textcoords="offset points",
                fontsize=9, color=INK_2, ha="right")
    ax.plot(x[-1], y[-1], "s", ms=8, color=ORANGE, mec=SURFACE, mew=1.5, zorder=5)
    ax.annotate("landing", (x[-1], y[-1]), xytext=(14, -18),
                textcoords="offset points", fontsize=9, color=INK_2)
    ax.set_aspect("equal")
    ax.set_xlabel("East [m]")
    ax.set_ylabel("North [m]")
    ax.set_title("Ground track", loc="left")
    cb = fig.colorbar(lc, ax=ax, shrink=0.8, pad=0.02)
    cb.set_label("altitude AGL [m]", color=INK_2, fontsize=9)
    cb.ax.tick_params(colors=MUTED, labelsize=8)
    cb.outline.set_edgecolor(BASELINE)
    fig.savefig(outdir / "ground_track.png", bbox_inches="tight")
    plt.close(fig)


def fig_transition(span, win, outdir):
    att = crop(load("ATT", span), win)
    out0 = crop(load("OUT0", span), win)

    fig, axes = plt.subplots(2, 1, figsize=(11, 6.4), dpi=150, sharex=True)
    fig.subplots_adjust(hspace=0.35, top=0.9)
    fig.suptitle(
        "Attitude and lift-motor commands through the flight",
        fontsize=13, fontweight="bold", color=INK, x=0.07, ha="left",
    )

    ax = axes[0]
    ax.plot(att.t, np.degrees(att.ATT_Roll), color=BLUE, lw=1.6, label="roll")
    ax.plot(att.t, np.degrees(att.ATT_Pitch), color=ORANGE, lw=1.6, label="pitch")
    ax.axhline(0, color=BASELINE, lw=0.8, zorder=0)
    ax.set_ylabel("attitude [deg]")
    ax.set_title("Roll and pitch (ATT)", loc="left")
    ax.legend(loc="upper left", ncol=2)

    ax = axes[1]
    for i, color in enumerate([BLUE, ORANGE, AQUA, YELLOW]):
        ax.plot(out0.t, out0[f"OUT0_Out{i}"], color=color, lw=1.4,
                label=f"lift motor {i + 1}")
    ax.set_ylabel("PWM [µs]")
    ax.set_xlabel("session time [min]")
    ax.set_title("Multicopter lift-motor outputs (OUT0, ch 1-4)", loc="left")
    ax.legend(loc="upper center", ncol=4)

    fig.savefig(outdir / "transition.png", bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--outdir", type=Path, default=REPO / "figures")
    args = parser.parse_args()
    args.outdir.mkdir(parents=True, exist_ok=True)

    span = session_minutes()
    gpos = load("GPOS", span)
    win = flight_window(gpos)
    print(f"session {span:.2f} min, flight window {win[0]:.2f}-{win[1]:.2f} min")

    fig_overview(span, win, args.outdir)
    fig_trajectory_3d(span, win, args.outdir)
    fig_ground_track(span, win, args.outdir)
    fig_transition(span, win, args.outdir)
    print(f"wrote 4 figures to {args.outdir}")


if __name__ == "__main__":
    main()
