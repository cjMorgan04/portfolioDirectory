import serial
import serial.tools.list_ports

def read_serial_string(port_name, baud_rate=9600):
    try:
        # Open port with a 2-second timeout so it doesn't freeze forever if no data arrives
        with serial.Serial(port=port_name, baudrate=baud_rate, timeout=2) as ser:
            # Read one line of bytes
            raw_data = ser.readline() 
            
            # Convert bytes to string and strip whitespace (\r\n)
            return raw_data.decode('utf-8').strip()
            
    except serial.SerialException as e:
        return f"Error: {e}"


def list_available_ports():
    """Lists all active serial ports connected to the computer."""
    ports = serial.tools.list_ports.comports()
    print("Available ports:")
    for port in ports:
        print(f" - {port.device}: {port.description}")
    print("")

def start_monitor(port_name, baud_rate):
    """Connects to and monitors a specific serial port."""
    print(f"Connecting to {port_name} at {baud_rate} baud...")
    
    try:
        # Initialize serial connection with a timeout to prevent hanging
        with serial.Serial(port=port_name, baudrate=baud_rate, timeout=1) as ser:
            print(f"Connected successfully! Monitoring {port_name}... Press Ctrl+C to stop.\n")
            
            # Flush buffers to clear older data
            ser.reset_input_buffer()
            
            while True:
                # Read a line of data if available
                if ser.in_waiting > 0:
                    raw_data = ser.readline()
                    
                    try:
                        # Decode binary bytes into a readable string
                        decoded_data = raw_data.decode('utf-8').strip()
                        print(f"[DATA]: {decoded_data}")
                    except UnicodeDecodeError:
                        # Fallback for binary data packets
                        print(f"[RAW BYTES]: {raw_data}")
                        
    except serial.SerialException as e:
        print(f"\nError: Could not open port {port_name}. {e}")
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user.")

