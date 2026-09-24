import time
import matplotlib.pyplot as plt
from serialMonitor import read_serial_string
from SPD1305X import VisaClose, VisaConnect, VisaQuery, VisaWrite

class PID:
    def __init__(self, setpoint=0, pv=0, previous_error=0, integral=0, dt=0):
        self.setpoint = setpoint
        self.pv = pv
        self.kp = 0
        self.ki = 0
        self.kd = 0
        self.previous_error = previous_error
        self.integral = integral
        self.dt = dt


    def pid_controller(self):
        self.error = self.setpoint - self.pv
        self.integral += self.error * self.dt
        self.derivative = (self.error - self.previous_error) / self.dt
        control = self.kp * self.error + self.ki * self.integral + self.kd * self.derivative
        return control, self.error, self.integral

    def simulation(self):
        print("Starting Run...")
        time_steps = []
        pv_values = []
        control_values = []
        setpoint_values = []
        try:
            for i in range(100):  # Simulate for 100 time steps
                control, error, integral = self.pid_controller(self.setpoint, self.pv, self.kp, self.ki, self.kd, self.previous_error, self.integral, self.dt)
                pv += control * self.dt  # Update process variable based on control output (simplified)
                previous_error = error

                time_steps.append(i * self.dt)
                pv_values.append(pv)
                control_values.append(control)
                setpoint_values.append(self.setpoint)

                time.sleep(self.dt)
                plt.figure(figsize=(12, 6))
                    
            plt.subplot(2, 1, 1)
            plt.plot(time_steps, pv_values, label='Process Variable (PV)')
            plt.plot(time_steps, setpoint_values, label='Setpoint', linestyle='--')
            plt.xlabel('Time (s)')
            plt.ylabel('Value')
            plt.title('Process Variable vs. Setpoint')
            plt.legend()
                
            plt.subplot(2, 1, 2)
            plt.plot(time_steps, control_values, label='Control Output')
            plt.xlabel('Time (s)')
            plt.ylabel('Control Output')
            plt.title('Control Output over Time')
            plt.legend()
                
            plt.tight_layout()
            plt.show()
        except KeyboardInterrupt:
            print("Run Stopped By User")
        


