import matplotlib.pyplot as plt
import numpy as np

def choose_window(window,N):
	if window=='hanning':
		w=np.hanning(N)
	elif window=='hanning4':
		# special for LLRF board testing, ignore first four data points
		w=np.concatenate((np.array([0]*4),np.hanning(N-4)))
	elif window=='hft116d':
		w=hft116d(N)
	elif window=='hamming':
		w=np.hamming(N)
	else:
		w=np.ones(N)
	return w

def iq_data(path_to_file):
	print "IQ data loading..."
	data = np.loadtxt(path_to_file)
	print "Number of data points in the time series N = %s" %len(data)
	data = data.transpose()
	magA = np.abs(data[0] + 1j*data[1])
	magB = np.abs(data[2] + 1j*data[3])
	return (magA,magB)

def fft(y,fs,window='hanning'):
	N=len(y)
	#y=np.array(y)
	print "Frequency Resolution Fs = %f Hz" %(fs/N)
	freqs=np.arange(0,fs,fs*1.0/N)
	w = choose_window(window,N)
	s0 = sum(w)
	s1 = s0**2
	s2 = sum(w*w)
	y = y - sum(w*y)/s0  # remove DC component for real
	NENBW = N*s2/(s1**2)
	ENBW = fs*s2/(s1**2)
	fft_y_win = np.fft.fft(y*w)
	prod = abs(fft_y_win)**2
	ps = 2.0/s1 * prod
	psd = 2.0/s2/fs * prod
	ls = np.sqrt(ps)
	lsd = np.sqrt(psd)
	return [freqs[1:N/2],ps[1:N/2],psd[1:N/2], fft_y_win,NENBW,ENBW,ls[1:N/2],lsd[1:N/2],s1,s2]

def	maximum_values(ls,scale):
        print max(ls)
        print np.argmax(ls)*scale
        print max(ls[4697:9395])
        print (np.argmax(ls[4697:9395])+4697)*scale
        print max(ls[9395:18800])
        print (np.argmax(ls[9395:18800])+9395)*scale

if __name__=="__main__":
	[A,B] = iq_data('./total_PRC_closeto_fan_ON')
	cic_period = 8448
	cic_shift = 14
	LO = 1320e6
	fs =  LO/(cic_period * cic_shift) 
	print "Sampling frequency Fs = %f Hz" %fs 
	[freqs,A_ps,A_psd,A_fft_win,NENBW,ENDW,A_ls,A_lsd,s1,s2]=fft(A,fs)
	[freqs,B_ps,B_psd,B_fft_win,NENBW,ENDW,B_ls,B_lsd,s1,s2]=fft(B,fs)

	maximum_values(A_ls,fs/len(A))

	prod = B_fft_win * np.conj(A_fft_win) #Cross corelation
	prod = prod[1:len(prod)/2]
	xps = 2.0/s1 * prod
        xpsd = 2.0/s2/fs * prod
        xls = np.sqrt(xps)
        xlsd = np.sqrt(xpsd)

	#frequency lower and upper limits for the plots. 
	ll = 0
	ul = 50000 # 1048576 is the highest limit

	#Plotting
	f, ((ax1,ax2,ax3),(ax4,ax5,ax6),(ax7,ax8,ax9),(ax10,ax11,ax12)) = plt.subplots(4,3, sharex='col',sharey='row')
	ax1.semilogy(freqs[ll:ul],A_ls[ll:ul])
        ax4.semilogy(freqs[ll:ul],A_lsd[ll:ul])
        ax7.semilogy(freqs[ll:ul],A_ps[ll:ul])
        ax10.semilogy(freqs[ll:ul],A_psd[ll:ul])
        ax2.semilogy(freqs[ll:ul],B_ls[ll:ul])
        ax5.semilogy(freqs[ll:ul],B_lsd[ll:ul])
        ax8.semilogy(freqs[ll:ul],B_ps[ll:ul])
        ax11.semilogy(freqs[ll:ul],B_psd[ll:ul])
        ax3.semilogy(freqs[ll:ul],xls[ll:ul])
        ax6.semilogy(freqs[ll:ul],xlsd[ll:ul])
        ax9.semilogy(freqs[ll:ul],xps[ll:ul])
        ax12.semilogy(freqs[ll:ul],xpsd[ll:ul])
        ax1.set_title('Channel 1')
        ax2.set_title('Channel 2')
	ax3.set_title('Cross-corelation')
        ax1.set_ylabel('Linear Spectrum')
        ax4.set_ylabel('Linear Spectral Density')
        ax7.set_ylabel('Power Spectrum')
        ax10.set_ylabel('Power Spectrum Density')
	ax10.set_xlabel('Hz')
        ax11.set_xlabel('Hz')
	ax12.set_xlabel('Hz')

	plt.show()

        [A,B] = iq_data('./total_PRC_closeto_fan_ON')
        [C,D] = iq_data('./total_PRC_closeto_fan_OFF')
        [E,F] = iq_data('./total_06192017_fanON')
        [G,H] = iq_data('./total_06192017_fanOFF')

	[freqs,A_ps,A_psd,A_fft_win,NENBW,ENDW,A_ls,A_lsd,s1,s2]=fft(A,fs)
	maximum_values(A_ls,fs/len(A))
	[freqs,C_ps,C_psd,C_fft_win,NENBW,ENDW,C_ls,C_lsd,s1,s2]=fft(C,fs)
	maximum_values(C_ls,fs/len(C))
	[freqs,E_ps,E_psd,E_fft_win,NENBW,ENDW,E_ls,E_lsd,s1,s2]=fft(E,fs)
	maximum_values(E_ls,fs/len(E))
	[freqs,G_ps,G_psd,G_fft_win,NENBW,ENDW,G_ls,G_lsd,s1,s2]=fft(G,fs)
	maximum_values(G_ls,fs/len(G))

	#Plotting
        f, ((ax1,ax2),(ax3,ax4)) = plt.subplots(2,2, sharex='col',sharey='row')
        ax1.semilogy(freqs[ll:ul],A_ls[ll:ul])
        ax2.semilogy(freqs[ll:ul],C_ls[ll:ul])
        ax3.semilogy(freqs[ll:ul],E_ls[ll:ul])
        ax4.semilogy(freqs[ll:ul],G_ls[ll:ul])

	ax1.set_title('Fan ON')
        ax2.set_title('Fan OFF')
        ax1.set_ylabel('PRC close to fan')
        ax3.set_ylabel('PRC away from fan')
        ax3.set_xlabel('Hz')
        ax4.set_xlabel('Hz')

	plt.show()
