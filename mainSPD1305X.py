import time
from SPD1305X import VisaClose, VisaConnect, VisaQuery, VisaWrite
from serialMonitor import read_serial_string
# --- CONFIGURATION (Safe & Gentle Ramp) ---
USB_RESOURCE = ""  # Leave empty for auto-detect

# Low power limits to protect thermocouple and aluminum block
MAX_VOLTAGE = 5.0  # Capped at 5.0 V (Adjustable)
START_CURRENT = 0.0  # Start at 0.000 Amps
END_CURRENT = 0.5  # Max current target in Amps (5.0V * 0.5A = 2.5 Watts max output)

RAMP_MINUTES = 30.0  # Duration of the ramp in minutes
RAMP_SECONDS = RAMP_MINUTES * 60.0  # Total ramp time in seconds (1800s)
STEP_INTERVAL = 1.0  # Update frequency in seconds

#Set targets (Adjust these to match your device)
TARGET_PORT = "COM4"      # Windows template
# TARGET_PORT = "/dev/ttyACM0"  # Linux/Mac template
TARGET_BAUD = 5000000

inst = VisaConnect(USB_RESOURCE)

try:
    # 1. Initialize power supply limits
    VisaWrite(inst, f"CH1:VOLT {MAX_VOLTAGE:.3f}")
    VisaWrite(inst, f"CH1:CURR {START_CURRENT:.3f}")

    # 2. Enable channel output
    VisaWrite(inst, "OUTP CH1,ON")
    print(
        f"Output ON. Ramping current: {START_CURRENT:.3f}A -> {END_CURRENT:.3f}A over {RAMP_MINUTES} mins."
    )
    print(f"Voltage Limit: {MAX_VOLTAGE}V | Max Power Cap: {MAX_VOLTAGE * END_CURRENT:.2f}W\n")

    start_time = time.perf_counter()
    count = 0

    # 3. Live Ramping Loop
    while True:
        elapsed_time = time.perf_counter() - start_time

        # Calculate exact target current based on elapsed progress
        if elapsed_time < RAMP_SECONDS:
            progress = elapsed_time / RAMP_SECONDS
            current_setpoint = START_CURRENT + progress * (END_CURRENT - START_CURRENT)
        else:
            current_setpoint = END_CURRENT  # Hold at max power once 30 mins complete

        # Write updated current limit to the power supply
        VisaWrite(inst, f"CH1:CURR {current_setpoint:.3f}")

        # Query live values
        p_meas = VisaQuery(inst, "MEAS:POWE? CH1")
        v_meas = VisaQuery(inst, "MEAS:VOLT?")
        i_meas = VisaQuery(inst, "MEAS:CURR?")
        temperature = read_serial_string(TARGET_PORT, TARGET_BAUD)

        elapsed_min = elapsed_time / 60.0
        print(
            f"[{count:04d}] Time: {elapsed_min:05.2f}m / {RAMP_MINUTES}m | "
            f"Set: {current_setpoint:.3f}A | "
            f"Live: {p_meas.strip()} W ({v_meas.strip()} V, {i_meas.strip()} A) "
            f"{temperature}"
        )

        count += 1
        time.sleep(STEP_INTERVAL)

except KeyboardInterrupt:
    print("\n\nHeating process interrupted by user.")

finally:
    # Safety shutdown: Drop current to 0 and turn output off
    print("Safely shutting down: Zeroing current and turning OFF output...")
    VisaWrite(inst, "CH1:CURR 0.000")
    VisaWrite(inst, "OUTP CH1,OFF")
    VisaClose(inst)