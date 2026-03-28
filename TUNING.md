# Tuning Guide

All PID gains listed here are live-tunable via SmartDashboard. Edit the value in the dashboard and it takes effect immediately — no redeploy needed. Once you find good values, update the constants in source code.

---

## Face Hopper (Heading Controller)

Auto-rotates the robot to point at the alliance hopper while the driver controls translation. Activated by pressing the right stick (R3).

**Source:** `robotcontainer.py`
**Default values:** P=7.0, I=0, D=0

### SmartDashboard Keys

All update continuously (not just when R3 is pressed):

| Key | Type | Description |
|-----|------|-------------|
| `FaceHopper/kP` | Tunable | Proportional gain — rotation speed per degree of error |
| `FaceHopper/kI` | Tunable | Integral gain — corrects persistent small errors |
| `FaceHopper/kD` | Tunable | Derivative gain — dampens overshoot |
| `FaceHopper/TargetDeg` | Read-only | Angle the robot should face to point at the hopper |
| `FaceHopper/CurrentDeg` | Read-only | Angle the robot is actually facing |
| `FaceHopper/ErrorDeg` | Read-only | Difference (should be ~0 when locked on) |

### What Good Looks Like

When R3 is pressed, `ErrorDeg` drops to near zero within 0.3-0.5 seconds and stays small (under ~5 degrees) as the robot drives around.

### Symptoms and Fixes

| Symptom | Cause | Fix |
|---------|-------|-----|
| Sluggish rotation, large steady error | P too low | Increase kP (try 10, 12) |
| Oscillates/wobbles around target | P too high | Decrease kP (try 4, 5) or add kD (0.1-0.5) |
| Overshoots then corrects back | No damping | Add kD (try 0.2-0.5) |
| Settles close but not exactly on target | No integral term | Add small kI (try 0.1) — careful, can cause windup |
| Robot spins the long way around | Continuous input broken | Check code has `enableContinuousInput(-pi, pi)` |

### Tuning Procedure

1. Place the robot facing roughly 90 degrees away from the hopper
2. Press R3 and watch `ErrorDeg` — it should converge to zero
3. If it overshoots and oscillates, add kD before reducing kP
4. Drive around with R3 held — the error should stay small while translating
5. Test from multiple positions and angles on the field

---

## Launcher (Velocity Controller)

The launcher uses a Phoenix 6 TalonFX velocity controller. Unlike a standard PID, it uses **feedforward gains** (kV, kS) to do most of the work, with kP correcting the remaining error.

**Source:** `subsystems/launcher.py`
**Default values:** kP=0.1, kV=0.15, kS=0.0

### How the Gains Work

| Gain | What it does | Think of it as... |
|------|-------------|-------------------|
| **kV** | Voltage per RPS of target velocity. This is the main gain — it sets the baseline voltage needed to spin at a given speed. | "How much gas to cruise at this speed" |
| **kS** | Constant voltage to overcome static friction. Applied whenever the motor should be moving. | "How much gas just to start rolling" |
| **kP** | Voltage per RPS of error. Corrects the difference between target and actual speed. | "How hard to push when you're behind" |

### SmartDashboard Keys

| Key | Type | Description |
|-----|------|-------------|
| `Launcher/kP` | Tunable | Proportional gain |
| `Launcher/kV` | Tunable | Velocity feedforward |
| `Launcher/kS` | Tunable | Static friction feedforward |
| `Launcher/TargetRPS` | Read-only | Active target speed (auto or manual) |
| `Launcher/ActualRPS` | Read-only | Measured flywheel speed |
| `Launcher/ErrorRPS` | Read-only | Target minus actual (positive = too slow) |
| `Launcher/AtTarget` | Read-only | True when within 2 RPS of target |
| `Launcher/SpinUpTimeSec` | Read-only | Time from first movement to reaching target (updates each spin-up) |
| `Launcher/DistanceToHopper` | Read-only | Distance from robot to alliance hopper (meters) |
| `Launcher/Mode` | Read-only | "Auto" (distance-based) or "Manual" |

### What Good Looks Like

- `ErrorRPS` settles to within +/-2 RPS quickly (under 1 second)
- `SpinUpTimeSec` is as low as possible (this is your launch delay)
- `ActualRPS` holds steady under load (when balls are fed through)
- No oscillation in `ActualRPS` when at steady state

### Tuning Procedure

**Step 1 — Set kV (do this first, it matters most):**
1. Set kP=0, kS=0 so only feedforward is active
2. Command a target (e.g. 54 RPS) and look at `ActualRPS`
3. If actual is lower than target, increase kV. If higher, decrease kV
4. Goal: kV alone gets you within ~10% of the target speed
5. Rough formula: kV = battery_voltage / free_speed_rps (around 0.12-0.18 for a Falcon)

**Step 2 — Set kS (optional, helps at low speeds):**
1. With kP still at 0, command a low target (e.g. 10 RPS)
2. If the motor struggles to start or is sluggish from rest, increase kS (try 0.1-0.3)
3. kS should be just enough to overcome friction — too high and it will overshoot at low speeds

**Step 3 — Set kP (clean up the remaining error):**
1. Restore kP (start at 0.1)
2. Command your target and watch `ErrorRPS` — it should converge to near zero
3. If it oscillates, reduce kP. If error lingers, increase kP
4. Feed a ball through while watching `ActualRPS` — the speed will dip; kP is what recovers it

### Measuring Spin-Up Performance

`SpinUpTimeSec` updates every time the launcher goes from stopped to at-target. To measure:
1. Stop the launcher (let `ActualRPS` drop to zero)
2. Command the target speed
3. Wait for `AtTarget` to show True
4. Read `SpinUpTimeSec` — this is how long your autonomous would need to wait before feeding

Compare this value across different gain settings to find the fastest spin-up without overshoot. For autonomous, this directly determines how long to wait before activating the feeder.
