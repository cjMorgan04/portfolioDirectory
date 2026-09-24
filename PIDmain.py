from PIDfunctions import PID
from serialMonitor import read_serial_string

run = True 
userChoice = None

while(run):
    input(
        "1. Print Current Temp\n"
        "2. Set New Temp\n"
        "Enter Choice:"
    )
    userChoice = input()

    match userChoice:
        case 1:
            print(read_serial_string(TARGET_PORT, TARGET_BAUD)) 
        case 2: 
            
            