# Telemetry data dictionary

Column-level reference for the 13 PX4 topic exports in [`data/telemetry/`](../data/telemetry/).

**Source log:** `log_5_2022-9-4-18-02-56.px4log` — PX4 v1.7.0, legacy `sdlog2`
binary format, extracted per-topic with `sdlog2_dump.py` from the
[PX4-Autopilot v1.7.0](https://github.com/PX4/PX4-Autopilot/tree/v1.7.0) release tag.

**Session:** 24.02 min total (bounded by the `GPS_GPSTime` microsecond clock),
of which the final ~6 min is the actual flight (arm → VTOL take-off →
transition → fixed-wing cruise → back-transition → landing).

**Time base:** the CSV rows do not carry a per-row timestamp column. Each topic
is logged at an approximately fixed rate while the logger runs, so a uniform
time axis over the 24.02-min session (as done in
[`analysis/plot_flight.py`](../analysis/plot_flight.py)) is accurate to within
scheduler jitter — sufficient for visualisation and phase-level analysis, not
for spectral/rate-sensitive work. The "rate" column below is simply
`rows / session length`.

Angles are radians, positions metres, velocities m/s, following PX4 `sdlog2`
conventions (NED frame: X north, Y east, Z **down**).

---

## ATT — vehicle attitude (~22 Hz, 31 885 rows)

| Column | Meaning |
|---|---|
| `ATT_qw, ATT_qx, ATT_qy, ATT_qz` | Attitude quaternion (body → NED) |
| `ATT_Roll, ATT_Pitch, ATT_Yaw` | Euler angles [rad] |
| `ATT_RollRate, ATT_PitchRate, ATT_YawRate` | Body angular rates [rad/s] |
| `ATT_GX, ATT_GY, ATT_GZ` | Estimated ground-relative velocity components (unused in this log) |

## ATSP — attitude setpoint (~22 Hz, 31 746 rows)

| Column | Meaning |
|---|---|
| `ATSP_RollSP, ATSP_PitchSP, ATSP_YawSP` | Commanded Euler angles [rad] |
| `ATSP_ThrustSP` | Normalised thrust setpoint [0–1] |
| `ATSP_qw…ATSP_qz` | Setpoint quaternion |
| `ATSP_fwy, ATSP_dmcy, ATSP_af, ATSP_tm, ATSP_eon, ATSP_di` | Controller flags (fw yaw-wheel, disable mc yaw, apply flaps, thrust-major, enabled, direct-input) |

## ARSP — attitude *rate* setpoint (~86 Hz, 123 738 rows)

| Column | Meaning |
|---|---|
| `ARSP_RollRateSP, ARSP_PitchRateSP, ARSP_YawRateSP` | Commanded body rates [rad/s] — inner-loop setpoints |

> Note: despite the name, `ARSP` in `sdlog2` is the attitude-**rate** setpoint
> topic, not airspeed. Airspeed is in `AIRS`.

## AIRS — airspeed (~1 Hz, 1 445 rows)

| Column | Meaning |
|---|---|
| `AIRS_IndSpeed` | Indicated airspeed [m/s] |
| `AIRS_TrueSpeed` | True airspeed [m/s] |
| `AIRS_AirTemp` | Air temperature [°C] |
| `AIRS_Conf` | Sensor confidence [0–1] |

## LPOS — local position estimate (~22 Hz, 31 157 rows)

| Column | Meaning |
|---|---|
| `LPOS_X, LPOS_Y, LPOS_Z` | Local NED position [m] (Z positive **down**) |
| `LPOS_Dist, LPOS_DistR` | Distance-sensor reading and rate |
| `LPOS_VX, LPOS_VY, LPOS_VZ` | NED velocity [m/s] |
| `LPOS_RLat, LPOS_RLon, LPOS_RAlt` | Local-frame reference origin (lat/lon/alt) |
| `LPOS_PFlg, LPOS_GFlg` | Position / ground-distance validity flags |
| `LPOS_EPH, LPOS_EPV` | Horizontal / vertical position std-dev [m] |

## LPSP — local position setpoint (event, 6 599 rows)

| Column | Meaning |
|---|---|
| `LPSP_X, LPSP_Y, LPSP_Z, LPSP_Yaw` | Position + yaw setpoint |
| `LPSP_VX, LPSP_VY, LPSP_VZ` | Velocity setpoint [m/s] |
| `LPSP_AX, LPSP_AY, LPSP_AZ` | Acceleration setpoint [m/s²] |

## GPOS — global position estimate (~22 Hz, 31 010 rows)

| Column | Meaning |
|---|---|
| `GPOS_Lat, GPOS_Lon` | WGS-84 latitude / longitude [deg] |
| `GPOS_Alt` | Altitude AMSL [m] |
| `GPOS_VelN, GPOS_VelE, GPOS_VelD` | NED velocity [m/s] |
| `GPOS_EPH, GPOS_EPV` | Position accuracy estimates [m] |
| `GPOS_TALT` | Terrain altitude [m] (−1 = invalid) |

## GPS — raw GNSS (~1 Hz, 1 484 rows)

| Column | Meaning |
|---|---|
| `GPS_GPSTime` | GPS epoch time [µs] — **the only absolute clock in the dataset** |
| `GPS_Fix` | Fix type (4 = 3D-RTK class fix in this log) |
| `GPS_EPH, GPS_EPV` | Horizontal / vertical accuracy [m] |
| `GPS_Lat, GPS_Lon, GPS_Alt` | Raw receiver position |
| `GPS_VN, GPS_VE, GPS_VD` | Receiver NED velocity [m/s] |
| `GPS_Cog` | Course over ground [rad] |
| `GPS_nSat` | Satellites used |
| `GPS_SNR, GPS_N, GPS_J, GPS_H` | Signal metrics (noise, jamming indicator/level) |

## OUT0 — actuator outputs, main bank (~10 Hz, 13 792 rows)

| Column | Meaning |
|---|---|
| `OUT0_Out0 … OUT0_Out3` | Quad lift-motor PWM [µs] (900 = off, ≈1150 = armed idle) |
| `OUT0_Out4 … OUT0_Out7` | Remaining main-bank channels (fixed-wing surfaces / pusher) |

## RC — pilot radio input (~9 Hz, 13 534 rows)

| Column | Meaning |
|---|---|
| `RC_C0 … RC_C11` | Normalised channel values [−1 … 1] |
| `RC_RSSI` | Link signal strength |
| `RC_CNT, RC_Lost, RC_Drop` | Frame counter, link-lost flag, drop count |

## BATT — battery status (~1 Hz, 1 442 rows)

| Column | Meaning |
|---|---|
| `BATT_VFilt` | Filtered pack voltage [V] (6S Li-Po) |
| `BATT_CFilt` | Filtered current [A] |
| `BATT_Discharged` | Consumed charge [mAh] |
| `BATT_Remaining, BATT_RemainingV` | Remaining-capacity estimates [0–1] |
| `BATT_Warning` | Low-battery warning level |

## PWR — power-rail status (~1 Hz, 1 439 rows)

| Column | Meaning |
|---|---|
| `PWR_Periph5V, PWR_Servo5V` | 5 V peripheral / servo rail voltages [V] |
| `PWR_RSSI` | RSSI analog input |
| `PWR_UsbOk, PWR_BrickOk, PWR_ServoOk` | Power-source validity flags |
| `PWR_PeriphOC, PWR_HipwrOC` | Over-current flags |

## STAT — system status (event, 7 237 rows)

| Column | Meaning |
|---|---|
| `STAT_NavState` | Navigation/flight-mode state (0 = manual, 3 = mission/auto in this log) |
| `STAT_ArmS` | Arming state |
| `STAT_Failsafe` | Failsafe active flag |
| `STAT_Landed` | Land-detector output |
| `STAT_Load` | CPU load [0–1] |
