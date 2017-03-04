import vxi11
import pprint

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
for channel in range(7):
    RF_input.append([])
    if channel == 0:
        raw_input ("Press enter when ready to measure LO")
    else:
        raw_input ("Press enter when ready to measure channel:" + str(channel))
    for mark in range(4):
        meas = 1 if ((mark+1)==1 or (mark+1)==3) else 2
        instr.write("CALC1:PAR:SEL 'Meas" + str(meas) + "'")
        measurement = to_DB(float(instr.ask("CALC1:MARK" + str(mark+1) + ":Y?").split(",")[0]))
        RF_input[channel].append(measurement)
        print measurement

pprint.pprint(RF_input)
