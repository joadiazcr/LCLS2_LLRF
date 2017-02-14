import sys, time
from optparse import OptionParser
from pyModbusTCP.client import ModbusClient

def connectClient(ip):
    try:
        c = ModbusClient(host=ip, port=502, debug=True)
    except ValueError:
        print("Error with host or port params")

    if c.open():
        print ("Connected!")
    else:
        print ("Connection failed :(")
        sys.exit(1)

    return c

def readHoldingRegisters(c,address,registers):
    regs = c.read_holding_registers(address, registers)
    print("Register address #"+str(address)+":"+str(regs))
    return regs

def writeSingleRegister(c,address,value):
    w = c.write_single_register(address,value)
    print("Writing address #"+str(address)+" with value "+str(value)+": "+str(w))

def writeMultipleRegisters(c,address,value):
    w = c.write_multiple_registers(address,value)
    print("Writing address #"+str(address)+" with value "+str(value)+": "+str(w))

def closeClient(c):
    close = c.close()
    print ("Conecction is close? "+str(close))

def main():
    usage = "usage: %prog --address <IP> [options]"
    parser = OptionParser(usage=usage)
    parser.add_option("-a","--address", dest="address", default=None, help="Provide IP address of the SSA")
    (options, args) = parser.parse_args()

    if options.address is None:
        parser.error("Please provide IP address of the SSA")
        sys.exit(1)

    c = connectClient(options.address)

    faults = [1,1]
    while faults != [0,0]:
        writeSingleRegister(c,4,2) #Clear external faults
        writeSingleRegister(c,4,1) #Clear internal faults
        faults = readHoldingRegisters(c,13,2) #Read internal & external fault error codes
        time.sleep(1)
    print ("Faults cleared!")

    DC = 0
    while DC == 0:
        writeSingleRegister(c,1,1) #Enable DC
        DC = readHoldingRegisters(c,1,1) #Read DC
        time.sleep(1)
    print ("DC enabled!")

    RF = 0
    while RF == 0:
        writeSingleRegister(c,2,1) #Enable RF
        DC = readHoldingRegisters(c,2,1) #Read RF
        time.sleep(1)
    print ("RF enabled!")

    DCPS = 0
    while CDPS != 700:
        writeSingleRegister(c,3,700) #Set DCPS to 13.5V
        DC = readHoldingRegisters(c,3,1) #Read DCPS value
        time.sleep(1)
    print ("DCPS set to 700!")

    closeClient(c)

if __name__ == "__main__":
    main()
