import sys
import jack
import pygame
from numpy import fft, array, log2, zeros, nan

pygame.init()
size = (1024, 600)
display = pygame.display.set_mode(size)

jack.attach('colours')
jack.register_port('in', jack.IsInput)
jack.activate()
jack.connect('system:capture_1', 'colours:in')

def hue_to_rgb(hue):
	r, g, b = 0.0, 0.0, 0.0
	scaler = hue*6 % 1
	if (hue < 1/6.0): return 1, scaler, 0
	elif (hue < 2/6.0): return 1-scaler, 1, 0
	elif (hue < 3/6.0): return 0, 1, scaler
	elif (hue < 4/6.0): return 0, 1-scaler, 1
	elif (hue < 5/6.0): return scaler, 0, 1
	else: return 1, 0, 1-scaler

buff = jack.get_buffer_size()
rate = jack.get_sample_rate()
freqs = fft.fftfreq(buff, 1.0/rate)[1:buff/2]
hues = array([(log2(F) - log2(440)) % 1 for F in freqs])
freq_rgb = array([hue_to_rgb(h) for h in hues]).T
capture = zeros((1, buff), 'f')
dummy = zeros((0,0), 'f')


while True:
	try:
		jack.process(dummy, capture)
	except jack.InputSyncError:
		print 'Input Sync Errror'

	bins = array([abs(a)**2 for a in fft.rfft(capture[0, 1:-1])])[1:]
	bin_rgbs = freq_rgb * bins
	rgb = [min(255, int(round(sum(col)))) for col in bin_rgbs]
	print rgb
	display.fill(pygame.Color(*rgb), (0, 0, size[0], size[1]))
	pygame.display.update()






