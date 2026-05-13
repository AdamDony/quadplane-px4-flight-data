# Quadplane VTOL — Flight-Test Telemetry & CFD Data

Companion data and analysis files for the AIAA SciTech Forum 2027 paper:

> **Flight-Test Characterization and Design Implications of Hover-to-Forward-Flight Transition for a Small Quadplane VTOL Aircraft**
> Md Azizul Islam, Anika Tasneem, S. G. M. Hossain, Md Nur-A-Adam Dony
> AIAA SciTech Forum, 11–15 January 2027, Orlando, Florida. AIAA Paper 2027-XXXX *(submitted)*

This repository hosts the raw PX4 telemetry, derived CSV topic exports, Ansys Fluent CFD project files, structural FEA results, S1223 airfoil reference data, and the SolidWorks/AutoCAD geometry used in the paper.

---

## Quick map

| Folder of files | What it contains |
|---|---|
| `*.csv` | 15 PX4 telemetry topics extracted from the binary `sdlog2` log |
| `AnsysSimu*.JPG`, `AnsysContour/Streamline/Vector/Particles*.JPG`, `Wing2D*.JPG` | 2D Fluent results — pressure contours, streamlines, residuals |
| `15AoA*Gusted*MS{Lift,Drag}.jpg`, `*AoA*Degree8ms.JPG` | Gust-perturbation lift and drag time-histories |
| `Drag Plot.jpg`, `Lift Plot.jpg`, `LiftDrag.xlsx` | Aggregated polar data |
| `GustedWind.wbpj`, `GustedWingProjectANSYS.wbpj`, `*_files.zip` | Ansys Workbench projects |
| `Deform*Pa.JPG`, `*ElasticStrain*.JPG`, `*ElasticStress*.JPG`, `FEAWing_files.zip` | Wing structural FEA |
| `S1223*.xlsx`, `S1223*.docx` | S1223 airfoil coordinates and scripts at various chord scalings |
| `Arm.SLDPRT`, `Drawing1.dwg`, `Drawing1-Model.pdf` | CAD: wing/arm geometry and assembly drawing |
| `AIAA.zip` | Paper source bundle (LaTeX + figures + scripts) |

---

## 1. Flight-test telemetry (CSVs)

The flight analyzed in the paper is a ~24 min session recorded **4 September 2022** in an open agricultural field near **Dhaka, Bangladesh** (23.85° N, 90.51° E), of which ~6.5 min were armed. Source binary log: `log_5_2022-9-4-18-02-56.px4log` (PX4 v1.7.0, legacy `sdlog2` format). The per-topic CSVs were extracted with `sdlog2_dump.py` from the PX4-Autopilot v1.7.0 release tag and time-aligned by forward-filling `TIME_StartTime`.

| CSV | PX4 topic | Typical rate | Used for |
|---|---|---|---|
| `ATT.csv` | Attitude quaternion + body rates | ~250 Hz | Euler angles, p/q/r, transition body-rate peaks |
| `ATSP.csv` | Attitude setpoint | event | Pitch setpoint $\theta_{\mathrm{cmd}}$ |
| `AIRS.csv` | Indicated airspeed (calibrated) | ~1 kHz | Hover wind, $V_T$, $V_{T,\text{back}}$, cruise IAS |
| `ARSP.csv` | Raw airspeed-sensor differential pressure | ~1 kHz | Pitot diagnostics |
| `BATT.csv` | Pack voltage and current (filtered) | ~10 Hz | Per-phase electrical power and energy |
| `PWR.csv` | Power-module raw $V$, $I$ | ~10 Hz | Cross-check on `BATT` |
| `GPOS.csv` | Global position (lat/lon/alt) | ~5 Hz | Trajectory plots |
| `GPS.csv` | Raw GPS | ~5 Hz | Fix quality, satellite count |
| `LPOS.csv` | Local-NED position estimator | ~50 Hz | $V_N$, $V_E$, $V_D$, $V_h$, climb rate |
| `LPSP.csv` | Local-NED position setpoint | event | Setpoint tracking error |
| `OUT0.csv` | PWM channels 0–7 | ~50 Hz | MC lift-motor commands |
| `OUT1.csv` | PWM channels 8–15 | ~50 Hz | FW/auxiliary channels incl. rear motor, elevator (AUX2) |
| `RC.csv` | RC input | ~50 Hz | Pilot stick input cross-check |
| `STAT.csv` | System / VTOL status flags | event | `RwMode`, `TransMode` (mode and transition flags) |
| `VTOL.csv` | VTOL-specific state | event | Front/back transition timing |

> **Note.** Columns within each CSV preserve the original PX4 field names (e.g. `ATT_q0`, `ATT_q1`, ..., `BATT_V`, `BATT_C`). Refer to the PX4 v1.7.0 source for full field semantics: <https://github.com/PX4/PX4-Autopilot/tree/v1.7.0>.

---

## 2. CFD — Ansys Fluent (2D airfoil)

A 2D angle-of-attack sweep on the wing airfoil was performed in Ansys Fluent (2022 R2 / 2023 R1) with the SST $k$–$\omega$ turbulence model on a symmetric C-grid mesh ($y^+ \lesssim 1$), $V_\infty = 15$ m/s, $\rho = 1.225$ kg/m³, $\mu = 1.789\times10^{-5}$ Pa·s, inlet turbulence intensity 1%.

**Project files.** Open with Ansys Workbench (Fluent + Mechanical):

| File | Purpose |
|---|---|
| `GustedWingProjectANSYS.wbpj` | Main angle-of-attack sweep (–5° to +20°) |
| `GustedWingProjectANSYS_files.zip` | Supporting `_files/` directory archive |
| `GustedWind.wbpj` | Gust-perturbation cases at $\alpha = +15°$ |
| `FEAWing_files.zip` | Structural FEA Workbench archive |

**Pressure-field exports per AoA** (Section IV.A of the paper):

| Image | Angle of attack |
|---|---|
| `AnsysSimuMinus5AOALift.JPG`, `AnsysSimuMinus5AOADrag.JPG` | $\alpha = -5°$ |
| `AnsysSimu0AOA*.JPG` | $\alpha = 0°$ |
| `AnsysSimu5AOA*.JPG` | $\alpha = +5°$ |
| `AnsysSimu10AOA*.JPG` | $\alpha = +10°$ |
| `AnsysSimu15AOA*.JPG` | $\alpha = +15°$ |
| `AnsysSimu20AOA*.JPG` | $\alpha = +20°$ |

**Flow visualization** (Ansys Discovery preview solver, low-speed inflow):

| File | Description |
|---|---|
| `AnsysStreamline.JPG` | Streamline trace around the wing |
| `AnsysVector.JPG` | Velocity vector field |
| `AnsysDirectionFied.JPG` | Direction-field overlay |
| `AnsysParticles.JPG` | Particle traces |
| `AnsysContour.JPG` | Pressure contour |
| `Wing2D.JPG`, `Wing2DPlot.JPG` | 2D wing planform extracted from CAD |
| `Streamline_Ex.JPG`, `Residuals_Ex.JPG` | Convergence and post-processing diagnostics |
| `SetUp.JPG`, `SetUp1.jpg` | CFD case setup screenshots |

---

## 3. Gust-perturbation cases

Files named `15AoA{S}Gusted{G}MS{Lift|Drag}.jpg` record integrated lift or drag time-histories at base $\alpha = +15°$ with secondary parameter `S` (45 or 60, see below) and gust magnitude `G` ∈ {2, 4, 6, 8} m/s:

| Filename pattern | Meaning |
|---|---|
| `15AoA45Gusted{G}MS{Lift\|Drag}.jpg` | Base AoA $+15°$, secondary $45°$ orientation, gust $G$ m/s |
| `15AoA60Gusted{G}MS{Lift\|Drag}.jpg` | Base AoA $+15°$, secondary $60°$ orientation, gust $G$ m/s |

The $\sim$33% lift-drop result reported in Section IV.D of the paper (`fig15_gust_case.png`) is from the 2 m/s case at $\alpha = +15°$.

**Static polar exports** at fixed AoA + varying $V_\infty$:

| File | Condition |
|---|---|
| `Lift0AoA{A}Degree8ms.JPG` / `Drag0AoA{A}Degree8ms.JPG` | $\alpha = 0°$, secondary angle $A°$ ∈ {30, 45, 60, 90, 135}, $V_\infty = 8$ m/s |
| `Lift Plot.jpg`, `Drag Plot.jpg` | Aggregated lift and drag plots |
| `LiftDrag.xlsx` | Raw $C_L(\alpha)$, $C_D(\alpha)$ numerical exports — the data behind Fig. 13 in the paper |

---

## 4. Structural FEA (wing)

Static-pressure loading on the wing surface at three equivalent inflow pressures (100, 200, 300 Pa), reported only briefly in the paper but available here for follow-on work:

| File | Result |
|---|---|
| `Deform100Pa.JPG`, `Deform200Pa.JPG`, `Deform300Pa.JPG` | Total deformation contour at 100/200/300 Pa |
| `ElasticStrain200Pa.JPG`, `ElasticStress200Pa.JPG` | Equivalent (von-Mises) elastic strain and stress at 200 Pa |
| `NormalElasticStrain200Pa.JPG`, `NormalElasticStress200Pa.JPG` | Normal-direction strain and stress at 200 Pa |
| `FEAWing_files.zip` | Full Workbench Mechanical project |

---

## 5. Airfoil reference (S1223)

The wing uses a low-Re S1223 cambered section.

| File | Contents |
|---|---|
| `S1223.xlsx` | Baseline S1223 coordinates and panel mesh |
| `S1223.SCRIPT.docx`, `S12237ygt.docx`, `Skl7i781223_10inch.docx` | XFOIL / Fluent meshing scripts |
| `S1223_10inch.xlsx`, `S1223_10inch.docx` | Coordinates scaled to 10″ chord |
| `S1223_11_5inch.xlsx`, `S1223_11_5inch.docx` | Coordinates scaled to 11.5″ chord |
| `S1223_Winglet.xlsx` | Winglet planform points |

---

## 6. CAD geometry

| File | Software | Purpose |
|---|---|---|
| `Arm.SLDPRT` | SolidWorks part | Wing/arm 3D solid (used in `fig02_wing_cad*` of the paper) |
| `Drawing1.dwg` | AutoCAD | Assembly drawing |
| `Drawing1-Model.pdf` | PDF | Rasterized assembly drawing |
| `Captur*.JPG`, `Capture*.JPG`, `Capture*.PNG` | screenshots | Renderings used in the paper's wing-geometry figure (panels c–e) |

---

## 7. Paper source

| File | Contents |
|---|---|
| `AIAA.zip` | LaTeX source, compiled PDF, figures, figure-generation scripts |
| `ReadMe.docx` | Earlier project-notes file (kept for historical reference; this `README.md` supersedes it) |

---

## How to cite

If you use these data or build on the analysis, please cite the paper:

```bibtex
@inproceedings{islam2027quadplane,
  author    = {Islam, Md Azizul and Tasneem, Anika and Hossain, S. G. M. and Dony, Md Nur-A-Adam},
  title     = {Flight-Test Characterization and Design Implications of Hover-to-Forward-Flight Transition for a Small Quadplane {VTOL} Aircraft},
  booktitle = {AIAA SciTech Forum 2027},
  number    = {AIAA Paper 2027-XXXX},
  address   = {Orlando, FL},
  month     = jan,
  year      = {2027},
  note      = {Companion data: \url{https://github.com/AdamDony/quadplane-px4-flight-data}}
}
```

*(Replace `2027-XXXX` with the assigned AIAA paper number once available, and add the DOI when the proceedings are published.)*

---

## License

| Asset | License |
|---|---|
| Telemetry CSVs, figures, plots, FEA / CFD result images, airfoil coordinates | Creative Commons Attribution 4.0 (CC-BY-4.0) |
| Ansys Workbench project files (`*.wbpj`, `*_files.zip`) | © the authors; reuse permitted under CC-BY-4.0 attribution. Note that opening these files requires the user's own valid Ansys licence — no Ansys software is redistributed here. |
| Paper source (`AIAA.zip`) | © the authors; redistributable per AIAA author rights. |

A `LICENSE` file with the full CC-BY-4.0 text is recommended for the repository root.

---

## Reproducibility notes

- The PX4 firmware version is **v1.7.0**. Newer PX4 releases moved from the `sdlog2` binary format to ULog (`.ulg`); the parsing pipeline used here is specific to `sdlog2`. The `sdlog2_dump.py` script from the v1.7.0 release tag is needed to re-derive the CSVs from the original `.px4log`.
- Figures in the paper were produced by the Python scripts in `AIAA.zip` (`build_figures.py`, `build_hero.py`).
- The Ansys cases require Workbench 2022 R2 or 2023 R1 (or compatible) and an academic or commercial Fluent + Mechanical licence.


