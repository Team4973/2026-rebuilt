# 2026-Rebuilt Wiring Map

Physical wiring reference for FRC Team 4973's robot.

## Power Distribution Hub (REV-11-1850)

**CAN ID: 1**

The PDH has 20 high-current channels (0-19, up to 40A each) and 3 low-current switchable channels (20-22, up to 15A each).

### High-Current Channels (0-19)

| Channel | Device | OCPD | Wire Gauge | Notes |
|---------|--------|---------|------------|-------|
| 0 | *available* | - | - | |
| 1 | *available* | - | - | |
| 2 | *available* | - | - | |
| 3 | *available* | - | - | |
| 4 | *available* | - | - | |
| 5 | *available* | - | - | |
| 6 | *available* | - | - | |
| 7 | *available* | - | - | |
| 8 | *available* | - | - | |
| 9 | *available* | - | - | |
| 10 | *available* | - | - | |
| 11 | *available* | - | - | |
| 12 | *available* | - | - | |
| 13 | *available* | - | - | |
| 14 | *available* | - | - | |
| 15 | *available* | - | - | |
| 16 | *available* | - | - | |
| 17 | *available* | - | - | |
| 18 | TalonFX (CAN 30) | 40A | 12 AWG | Test motor |
| 19 | *available* | - | - | |

### Switchable Low-Current Channels (20-23)

| Channel | Device | OCPD | Notes |
|---------|--------|---------|-------|
| 20 | *available* | 15A |  |
| 21 | *available* | 15A |  |
| 22 | *available* | 15A |  |
| 23 | *available* | 10A |  |


## CAN Bus Devices

| CAN ID | Device | Type | Location |
|--------|--------|------|----------|
| 1 | Power Distribution Hub | REV-11-1850 | Main board |
| 30 | TalonFX | Motor controller | Test motor |
| 2 | Pigeon 2 | IMU | TBD |

## Network Devices

| IP Address | Device | Hostname | Notes |
|------------|--------|----------|-------|
| 10.49.73.1 | RoboRIO | roboRIO-4973-FRC.local | Default |
| 10.49.73.12 | Orange Pi 5 | photonvision.local | PhotonVision coprocessor |

**PhotonVision Web UI**: http://10.49.73.11:5800

## Voltage Regulators

| Name | Input Source | Output | Devices Powered |
|------|--------------|--------|-----------------|
| VRM-2 | PDH 12V low-current block (ch TBD) | 12V | Pigeon 2 IMU |

## Future Additions

### Motors (planned)
- [ ] Drive motors (4x TalonFX?)
- [ ] Intake motor
- [ ] Shooter motors

### Sensors (planned)
- [ ] Gyro/IMU
- [ ] Encoders
- [ ] Limit switches
- [ ] Vision camera

### Other
- [ ] Radio
- [ ] RoboRIO
- [ ] Voltage regulator module (VRM)

---

## Wiring Best Practices

1. **Label everything** - Use heat shrink labels on both ends of each wire
2. **Color coding**:
   - Red = +12V power
   - Black = Ground
   - Green = CAN High
   - Yellow = CAN Low
3. **Breaker sizing** - Match breaker to motor stall current (check specs)
4. **Wire gauge** - 12 AWG for motors, 18 AWG for sensors, 22 AWG for CAN
5. **Strain relief** - Secure wires so they don't pull on connectors
