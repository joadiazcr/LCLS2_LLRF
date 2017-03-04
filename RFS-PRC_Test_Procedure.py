import vxi11
import pprint
import csv
import subprocess

#-------------------SERIAL NUMBERS
serial_numbers = []
for component in range(6):
    serial_numbers.append([])
    for number in range(5):
        serial_numbers[component].append("--")

serial_numbers[0][0]="Component"
serial_numbers[0][1]="Part Number"
serial_numbers[0][2]="Serial Number"
serial_numbers[0][3]="digital Serial Number/bitfile name"
serial_numbers[0][4]="SLAC ID Number"
serial_numbers[1][0]="Chassis"
serial_numbers[2][0]="BMB7"
serial_numbers[3][0]="Digitizer board"
serial_numbers[4][0]="Down Converter"
serial_numbers[5][0]="Up Converter"

chassis_type = raw_input ("Please enter type of chassis to test(RFS or PRC): ")
while (chassis_type != 'RFS' and chassis_type != 'PRC'):
    chassis_type = raw_input("Please enter a valid type os chassis to test(RFS or PRC): ")
serial_numbers[1][2] = raw_input ("Please enter chassis serial number: ")
serial_numbers[1][4] = serial_numbers[1][2]
serial_numbers[2][2] = raw_input ("Please enter BMB7 serial number: ")
serial_numbers[2][4] = raw_input ("Please enter BMB7 SLAC ID number: ")
serial_numbers[3][2] = raw_input ("Please enter digitizer serial number: ")
serial_numbers[3][4] = raw_input ("Please enter digitizer SLAC ID number: ")
serial_numbers[4][2] = raw_input ("Please enter down converter serial number: ")
serial_numbers[4][4] = raw_input ("Please enter down converter SLAC ID number: ")
serial_numbers[5][2] = raw_input ("Please enter up converter serial number: ")
serial_numbers[5][4] = raw_input ("Please enter up converter SLAC ID number: ")

with open("output.csv", "wb") as f:
    writer = csv.writer(f)
    writer.writerows(serial_numbers)

print type(serial_numbers[2][3])
s = [[str(e) for e in row] for row in serial_numbers]
lens = [max(map(len, col)) for col in zip(*s)]
fmt = '\t'.join('{{:{}}}'.format(x) for x in lens)
table = [fmt.format(*row) for row in s]
print '\n'.join(table)


#-------------------TEST NETWORK CONNECTIVITY
raw_input ("\nPlease epress enter when ready to test network connectivity: ")
subprocess.call(["/sbin/arp", "-a"])


#------------------RF CHECKS
raw_input ("\nPlease epress enter when ready to perform RF checks: ")
UNIT = 1000 ** 3 #GHz

def to_GHz(amount):
    return "%.2f" % (amount / float(UNIT),)

def to_DB(amount):
    return "%.2f" % amount

instr = vxi11.Instrument("192.168.165.2")
print instr.ask("*idn?")

#Deletes the default trace
instr.write("SYSTem:FPRESet")

#Start MEasurements
instr.write("CALCulate1:PARameter:DEFine:EXT 'Meas1','S11'")
instr.write("CALCulate1:PARameter:DEFine:EXT 'Meas2','S21'")
instr.write("DISPlay:WINDow1:STATE ON")
instr.write("DISPlay:WINDow1:TRACe1:FEED 'Meas1'")
instr.write("DISPlay:WINDow1:TRACe2:FEED 'Meas2'")

#Set frequency parameters
instr.write("SENSe1:FREQuency:CENTer 1300mhz")
instr.write("SENSe1:FREQuency:SPAN 200mhz")
#AKS about the sweep time

#Set markers
instr.write("CALC1:PAR:SEL 'Meas1'")
instr.write("CALC1:MARK1:STAT ON")
instr.write("CALC1:MARK1:X 1.3ghz")
instr.write("CALC1:MARK3:STAT ON")
instr.write("CALC1:MARK3:X 1.32ghz")
instr.write("CALC1:PAR:SEL 'Meas2'")
instr.write("CALC1:MARK2:STAT ON")
instr.write("CALC1:MARK2:X 1.3ghz")
instr.write("CALC1:MARK4:STAT ON")
instr.write("CALC1:MARK4:X 1.32ghz")

RF_input = []
for component in range(8):
    RF_input.append([])
    for number in range(5):
        RF_input[component].append("--")

RF_input[0][0] = "Input channel"
RF_input[1][0] = "LO"
RF_input[2][0] = "1"
RF_input[3][0] = "2"
RF_input[4][0] = "3"
RF_input[5][0] = "4"
RF_input[6][0] = "5"
RF_input[7][0] = "6"
RF_input[0][1] = "1300MHz-S11"
RF_input[0][2] = "1300MHz-S21"
RF_input[0][3] = "1320MHz-S11"
RF_input[0][4] = "1320MHz-S21"
for channel in range(7):
    #RF_input.append([])
    if channel == 0:
        raw_input ("Press enter when ready to measure LO")
    else:
        raw_input ("Press enter when ready to measure channel:" + str(channel))
    for mark in range(4):
        meas = 1 if ((mark+1)==1 or (mark+1)==3) else 2
        instr.write("CALC1:PAR:SEL 'Meas" + str(meas) + "'")
        measurement = to_DB(float(instr.ask("CALC1:MARK" + str(mark+1) + ":Y?").split(",")[0]))
        frequency = to_GHz(float(instr.ask("CALC1:MARK" + str(mark+1)+ ":X?")))
        RF_input[channel+1][mark+1] = measurement
        print frequency + "GHz " + measurement + "dB"

s  = [[str(e) for e in row] for row in RF_input]
lens = [max(map(len, col)) for col in zip(*s)]
fmt = '\t'.join('{{:{}}}'.format(x) for x in lens)
table = [fmt.format(*row) for row in s]
print '\n'.join(table)
