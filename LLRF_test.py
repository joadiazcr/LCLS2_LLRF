import numpy
import matplotlib.pyplot as plt
from prc import c_prc
from banyan_ch_find import banyan_ch_find
import time
import struct

#HOW TO PLOT
#x = np.linspace(0,10,10)
#fig, ax = plt.subplots()
#ax.plot(x, np.sin(x))
#plt.show()

# addr needs to be numeric
def pair_ram(prc, addr, count):
	foo = prc.reg_read_alist(range(addr, addr+count))
	uuu = [struct.unpack('!hh', x[2]) for x in foo]
	ram1 = [x[1] for x in uuu]
	ram2 = [x[0] for x in uuu]
	return [ram1, ram2]

def collect(prc, npt, print_minmax=True):
	prc.reg_write([{'rawadc_trig': 1}])
	(timestamp, minmax) = prc.slow_chain_readout()
	if print_minmax:
		print " ".join(["%d" % x for x in minmax]), "%.8f" % (timestamp*14/1320.0e6)
	while True:
		time.sleep(0.002)
		b_status = prc.reg_read_value(['banyan_status'])[0]
		# print "%8.8x"%b_status
		if not (b_status & 0x80000000): break
	astep = 1 << ((b_status >> 24) & 0x3F)
	addr_wave0 = prc.get_read_address('banyan_buf')
	value = []
	for ix in range(0, 8, 2):
		value.extend(pair_ram(prc, addr_wave0+ix*astep, npt))
	return (value, timestamp)

# nchans must be the result of len(banyan_ch_find())
def collect_adcs(prc, npt, nchans, print_minmax=True):
	(value, timestamp) = collect(prc, npt, print_minmax)
	# value holds 8 raw RAM blocks
	# block will have these assembled into ADC channels
	mult = 8/nchans
	block = []
	for ix in range(nchans):
		aaa = [value[jx] for jx in range(ix*mult, ix*mult+mult)]
		block.append(sum(aaa, []))
	return (block, timestamp)

RFS = '192.168.165.40'
PRC = '192.168.165.45'
port = 50006
mask = "0xff"
npt_wish = 0
verbose = True
freq = 145 #MHz
modulo = 136 #Magic number for LCLS-II
dac_mode = 0

prc_write = c_prc(RFS, port)
prc_read = c_prc(PRC, port)
b_status = prc_write.reg_read_value(['banyan_status'])[0]
npt = 1 << ((b_status >> 24) & 0x3F)
if npt == 1:
	print "aborting since hardware module not present"
	sys.exit(2)
mask_int = int(mask, 0)
# npt_wish only works correctly if mask is 0xff
if npt_wish and npt_wish < npt and mask_int == 0xff:
	npt = npt_wish
print "npt = %d" % npt
prc_write.reg_write([{'banyan_mask': mask_int}])
chans = banyan_ch_find(mask_int)
print chans, 8/len(chans)
nptx = npt*8/len(chans)
theta = numpy.array(range(nptx))*7*2*numpy.pi/33
basis = numpy.vstack((numpy.cos(theta), numpy.sin(theta), theta*0+1)).T
chan_txt = "column assignment for banyan_mask 0x%2.2x: " % mask_int + " ".join(["%d" % x for x in chans])

#Sweep on Amplitude
def amplitudeSweep(chassis_write, chassis_read, a_start, a_end, a_sweep, plot_pos):
	mat = numpy.zeros((8,33))
	for amplitude in range(a_start,a_end,a_sweep):
		#WRITE
		fclk = 1320.0 / 7.0  # DAC clock, 188.6 MHz
		ddsa = freq/fclk*2**20
		ddsa_phstep_h = int(ddsa)
		ddsa_phstep_l = int((ddsa - ddsa_phstep_h)*(4096-modulo) + 0.5)
		# print ddsa, ddsa_phstep_h, ddsa_phstep_l, fclk
		ferror = ddsa - ddsa_phstep_h - ddsa_phstep_l/(4096.0-modulo)
		ferror *= fclk*1e6/2.0**20
		print("Frequency error %.3f Hz" % ferror)
		vdict = {"ddsa_phstep_h":ddsa_phstep_h, "ddsa_phstep_l":ddsa_phstep_l, "ddsa_modulo":modulo}
		vdict["amplitude"] = amplitude
		vdict["dac_mode"] = dac_mode
		print vdict
		chassis_write.reg_write([vdict])
	
		#READ
		(block, timestamp) = collect_adcs(chassis_read, npt, len(chans))
		nblock = numpy.array(block).transpose()
		coeffzs = []
		amp = []
		for jx in range(len(chans) if verbose else 0):
			fit = numpy.linalg.lstsq(basis, nblock.T[jx])
			coeff = fit[0]
			coeffz = coeff[0]+1j*coeff[1]
			print_dbfs = numpy.log10(abs(coeffz)/32768.0)*20
			print "analysis %d  %7.1f  %7.2f dBFS  %7.2f degrees" % (jx, abs(coeffz), print_dbfs, numpy.angle(coeffz)*180/numpy.pi)
			coeffzs += [coeffz]
	        	amp += [abs(coeffz)]
	                mat[jx][amplitude/a_sweep] = abs(coeffz)
	#print mat
	plt.subplot(plot_pos)
	for i in range(mat.shape[0]):
		plt.plot(range(a_start,a_end,a_sweep), mat[i,:],label='Analysis %d' %i)
	plt.legend(loc='lower right')
	#plt.show()

#Sweep on frequency
def frequencySweep(chassis_write, chassis_read, f_start, f_end, f_sweep, plot_pos):
	amplitude = 32000
	mat_freq = numpy.zeros((8,f_end - f_start))
	for freq_count in range(f_start,f_end,f_sweep):
	        freq = freq_count/1000.0
	        #WRITE
	        fclk = 1320.0 / 7.0  # DAC clock, 188.6 MHz
	        ddsa = freq/fclk*2**20
	        ddsa_phstep_h = int(ddsa)
	        ddsa_phstep_l = int((ddsa - ddsa_phstep_h)*(4096-modulo) + 0.5)
	        # print ddsa, ddsa_phstep_h, ddsa_phstep_l, fclk
	        ferror = ddsa - ddsa_phstep_h - ddsa_phstep_l/(4096.0-modulo)
	        ferror *= fclk*1e6/2.0**20
	        print freq_count
	        print freq
	        print("Frequency error %.3f Hz" % ferror)
	        vdict = {"ddsa_phstep_h":ddsa_phstep_h, "ddsa_phstep_l":ddsa_phstep_l, "ddsa_modulo":modulo}
	        vdict["amplitude"] = amplitude
	        vdict["dac_mode"] = dac_mode
	        print vdict
	        chassis_write.reg_write([vdict])
	
	        #READ
	        (block, timestamp) = collect_adcs(chassis_read, npt, len(chans))
	        nblock = numpy.array(block).transpose()
	        coeffzs = []
	        amp = []
	        for jx in range(len(chans) if verbose else 0):
	                fit = numpy.linalg.lstsq(basis, nblock.T[jx])
	                coeff = fit[0]
	                coeffz = coeff[0]+1j*coeff[1]
	                print_dbfs = numpy.log10(abs(coeffz)/32768.0)*20
	                print "analysis %d  %7.1f  %7.2f dBFS  %7.2f degrees" % (jx, abs(coeffz), print_dbfs, numpy.angle(coeffz)*180/numpy.pi)
	                coeffzs += [coeffz]
	                amp += [abs(coeffz)]
	                mat_freq[jx][freq_count-f_start] = abs(coeffz)
	#print mat_freq
	plt.subplot(plot_pos)
	for i in range(mat_freq.shape[0]):
	        plt.plot(range(f_start,f_end,f_sweep), mat_freq[i,:],label='Analysis %d' %i)
                xlim(1, 50)
	plt.legend(loc='upper right')
	#plt.show()

#######RFS Amplitude Sweep
#amplitudeSweep(prc_write, prc_write, 0, 32001, 1000,221)
#plt.xlabel('Amplitude')
#plt.ylabel('Magnitude')
#plt.title('RFS Lecture - Amplitude Sweep')

######PRC Amplitude Sweep
#amplitudeSweep(prc_write, prc_read, 0, 32001, 1000,223)
#plt.xlabel('Amplitude')
#plt.ylabel('Magnitude')
#plt.title('PRC Lecture - Amplitude Sweep')

######RFS Frequency Sweep
frequencySweep(prc_write, prc_write, 144950, 145050, 1,222)
plt.xlabel('Frequency')
plt.ylabel('Magnitude')
plt.title('RFS Lecture - Frequency Sweep')

######PRC Frequency Sweep
#frequencySweep(prc_write, prc_read, 144950, 145050, 1,224)
#plt.xlabel('Frequency')
#plt.ylabel('Magnitude')
#plt.title('PRC Lecture - Frequency Sweep')

plt.show()
