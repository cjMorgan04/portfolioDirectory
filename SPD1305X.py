#Example code from siglent official user manual, originally designed for LAN, need usb
#Copied by Christopher Jones, Zhao Lab

import sys
import time
import pyvisa


def VisaConnect(resource_name=""):
    rm = pyvisa.ResourceManager()

    if not resource_name:
        resources = rm.list_resources("USB?*INSTR")
        if not resources:
            print("No USB VISA instruments found. Check USB connection.")
            sys.exit(1)
        resource_name = resources[0]
        print(f"Connected to: {resource_name}")

    try:
        inst = rm.open_resource(resource_name)
        inst.timeout = 5000
        inst.read_termination = "\n"
        inst.write_termination = "\n"
        return inst
    except pyvisa.VisaIOError as e:
        print(f"Failed to connect: {e}")
        sys.exit(1)


def VisaQuery(inst, cmd):
    try:
        reply = inst.query(cmd)
        time.sleep(0.05)
        return reply
    except pyvisa.VisaIOError:
        print("Query failed")
        sys.exit(1)


def VisaWrite(inst, cmd):
    try:
        inst.write(cmd) 
        time.sleep(0.05)
    except pyvisa.VisaIOError as e:
        print(f"Write failed ({cmd}): {e}")
        sys.exit(1)


def VisaClose(inst):
    if inst:
        inst.close()
        time.sleep(0.300)