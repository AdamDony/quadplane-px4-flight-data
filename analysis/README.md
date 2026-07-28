# Analysis toolkit

Reproduces every figure in [`figures/`](../figures/) directly from the raw
telemetry CSVs in [`data/telemetry/`](../data/telemetry/).

```bash
pip install -r analysis/requirements.txt
python analysis/plot_flight.py            # flight figures (run from the repo root)
python analysis/cfd_polars.py             # CFD polar reduction -> figures/cfd_polars.png
```

Output (≈10 s):

| Figure | Contents |
|---|---|
| `figures/flight_overview.png` | Altitude, ground speed + indicated airspeed, battery voltage, electrical power |
| `figures/trajectory_3d.png` | 3-D flight path (local NED), coloured by ground speed |
| `figures/ground_track.png` | Top-down ground track, coloured by altitude AGL |
| `figures/transition.png` | Roll/pitch and quad lift-motor PWM through both VTOL transitions |
| `figures/cfd_polars.png` | Finite-wing C_L/C_D polars and induced-drag fit reduced from `cfd/polars/LiftDrag.xlsx` |

## Time-base caveat

The `sdlog2` CSV exports carry no per-row timestamp; only `GPS.csv` has an
absolute clock (`GPS_GPSTime`, µs). The script assigns each topic a uniform
time axis spanning the GPS-derived 24.02-min session. This is good to within
logger scheduling jitter and is intended for visualisation and phase-level
interpretation — not for spectral analysis. See
[`docs/DATA_DICTIONARY.md`](../docs/DATA_DICTIONARY.md) for column semantics.
