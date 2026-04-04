# 2026-rebuilt

Team 4973's code for the 2026 "Rebuilt" FRC game, using RobotPy & CTRE Hardware.
## Device Ids
- 0 through 5: Misc Devices (PDH [0], IMU [2])
- 6 through 9: Swerve Turn Motors
- 10 through 13: Swerve CANCoders
- 16 through 19: Swerve Drive Motors
- 30 through 35: Arm/Intake/Shooter


## Robot Controls

| Control | Action |
|---------|--------|
| Left stick | Drive (field-centric X/Y velocity) |
| Right stick X | Rotation |
| A button (hold) | Brake mode |
| B button (hold) | Point wheels at joystick direction |
| X | Reset field-centric heading |

## Setup

### Option 1: uv (Recommended)

[uv](https://docs.astral.sh/uv/) manages Python and dependencies automatically - no global installs needed.

```bash
# Install uv (one time)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Run simulation (uv installs dependencies automatically)
uv run python -m robotpy sim
```

### Option 2: pip

If you prefer using system Python directly:

```bash
# Install dependencies
pip install robotpy[commands2,sim] phoenix6

# Run simulation
python3 -m robotpy sim
```

## Running Simulation

1. Run: `uv run python -m robotpy sim` (or `python3 -m robotpy sim` if using pip)
2. The simulation GUI opens
3. In the GUI:
   - Go to **Joysticks** panel
   - Map a virtual joystick to port 0
   - Enable **Teleop** mode
4. Test the controls:
   - Use left stick to drive
   - Use right stick to rotate
   - Press A to brake

## Deploying to Robot

When connected to the robot (via WiFi or USB):

```bash
# Using uv:
uv run python -m robotpy sync    # First time: sync dependencies to roboRIO
uv run python -m robotpy deploy  # Deploy code

# Or using pip:
python3 -m robotpy sync
python3 -m robotpy deploy
```

Then in Driver Station:
1. Connect to robot
2. Enable Teleop
3. Test controls

## Running Tests

```bash
# Using uv:
uv run python -m robotpy test

# Or using pip:
python3 -m robotpy test
```

## Troubleshooting

**Simulation won't start:**
- If using uv: try `uv sync --refresh` to reinstall dependencies
- If using pip: reinstall with `pip install --force-reinstall robotpy[commands2,sim] phoenix6`
- Check Python version: `python3 --version` (need 3.12+)

**Robot not responding in simulation:**
- Check the Joysticks panel - make sure a joystick is mapped to port 0
- Make sure Teleop is enabled (not Disabled or Autonomous)

**Deploy fails:**
- Make sure you're connected to the robot network
- Run sync first: `uv run python -m robotpy sync` (or `python3 -m robotpy sync`)
