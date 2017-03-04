import sys, time, csv
from optparse import OptionParser
from pyModbusTCP.client import ModbusClient

def connectClient(ip, verbose):
    try:
        c = ModbusClient(host=ip, port=502, debug=verbose)
    except ValueError:
        print("Error with host or port params")

    if c.open():
        print ("Connected!")
    else:
        print ("Connection failed :(")
        sys.exit(1)

    return c

def monitor (c):
    print "Monitoring"
    table = []
    table.append([])
    table[0].append("--")
    table[0].append("DC")
    table[0].append("RF")
    table[0].append("PS")
    table[0].append("AIR TEM")
    table[0].append("FAN ROT")  
    count = 0
    print '\t'.join(str(x) for x in table[count])
    while count < 5:
        regs = readHoldingRegisters(c,1, 3)
        regs = regs + (readHoldingRegisters(c,22, 2))
        regs.insert(0,count) 
        table.append(regs)
        time.sleep(2)
        count = count + 1
        print '\t'.join(str(x) for x in table[count])

    with open("monitor.csv", "wb") as f:
        writer = csv.writer(f)
        writer.writerows(table)

def readHoldingRegisters(c,address,registers):
    while True:
        if c.is_open():
            regs = c.read_holding_registers(address, registers)
            if regs:
                return regs
        else:
            c.open()

def writeSingleRegister(c,address,value):
    w = c.write_single_register(address,value)
    #print("Writing address #"+str(address)+" with value "+str(value)+": "+str(w))

def writeMultipleRegisters(c,address,value): 
    w = c.write_multiple_registers(address,value)
    #print("Writing address #"+str(address)+" with value "+str(value)+": "+str(w))

def closeClient(c):
    close = c.close()
    print ("\nConecction is close? "+str(close))

def main():
    usage = "usage: %prog --address <IP> [options]"
    parser = OptionParser(usage=usage)
    parser.add_option("-a","--address", dest="address", default=None, help="Provide IP address of the SSA")
    parser.add_option("-v","--verbose", action="store_true", dest="verbose", default=False, help="Verbose output")
    parser.add_option("-m","--monitor", action="store_true", dest="monitor", default=False, help="Monitoring mode of registers")
    (options, args) = parser.parse_args()

    if options.address is None:
        parser.error("Please provide IP address of the SSA")
        sys.exit(1)

    #Connect to the SSA
    c = connectClient(options.address, options.verbose)

    #Clear internal & esternal faults
    faults = []
    while faults != [0,0]:
        print "\nClearing internal and external faults..."
        writeSingleRegister(c,4,2) #Clear external faults
        writeSingleRegister(c,4,1) #Clear internal faults
        time.sleep(2)
        faults = readHoldingRegisters(c,13,2) #Read internal & external fault error codes
        if faults == [0,0]: break
        print "Internal and/or external faults error codes " + str(faults)
        raw_input ("Check the errors and press enter to try to clear faults again...")
    print ("\nFaults cleared!\n")

    #Enable DC
    DC = 0
    while DC != [1]:
        writeSingleRegister(c,1,1) #Enable DC
        time.sleep(2)
        DC = readHoldingRegisters(c,1,1) #Read DC 
    print ("\nDC enabled!\n")

    #Enable RF
    RF = 0 
    while RF != [1]:
        writeSingleRegister(c,2,1) #Enable RF
        time.sleep(2)
        RF = readHoldingRegisters(c,2,1) #Read RF
    print ("\nRF enabled!\n")

    #Set DCPS to 13.5V
    DCPS = 0
    while DCPS != [700]:
        writeSingleRegister(c,3,700) #Set DCPS to 13.5V
        time.sleep(2)
        DCPS = readHoldingRegisters(c,3,1) #Read DCPS value
    print ("\nDCPS set to 700!\n")

    #Monitoring mode
    if options.monitor == True : monitor(c)

    closeClient(c)

if __name__ == "__main__":
    main()
