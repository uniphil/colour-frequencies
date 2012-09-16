import sys
import numpy as np
import jack
from pylab import plot, show, draw, ion, xlim, ylim, xscale, bar, array, \
	log2, nan, average
import pygame
from pygame.locals import *

def hue_to_rgb(hue):
	r, g, b = 0.0, 0.0, 0.0
	scaler = hue*6 % 1
	if (hue < 1/6.0):
		r, g, b = 1, scaler, 0
	elif (hue < 2/6.0):
		r, g, b = 1-scaler, 1, 0
	elif (hue < 3/6.0):
		r, g, b = 0, 1, scaler
	elif (hue < 4/6.0):
		r, g, b = 0, 1-scaler, 1
	elif (hue < 5/6.0):
		r, g, b = scaler, 0, 1
	else:
		r, g, b = 1, 0, 1-scaler
	return r, g, b

jack.attach('colours')
jack.register_port('in', jack.IsInput)
jack.activate()
jack.connect('system:capture_1', 'colours:in')

buff = jack.get_buffer_size()
rate = jack.get_sample_rate()
freqs = np.fft.fftfreq(buff, 1.0/rate)[:buff/2]

hues = array([(log2(F) - log2(440)) % 1 for F in freqs])
hue_order = array(sorted(enumerate(hues[1:], 1), key=lambda f: f[1]), 'i').T[0]

freq_rgb = array([hue_to_rgb(h) for h in hues])
capture = np.zeros((1, buff), 'f')
dummy = np.zeros((0,0), 'f')

pygame.init()
size = (1024, 32)
window = pygame.display.set_mode(size)

ffact = size[0]/float(len(freqs))

while True:
	try:
		jack.process(dummy, capture)
	except jack.InputSyncError:
		print 'Input Sync'

	transformed = np.fft.rfft(capture[0][1:])

	#pygame.draw.rect(window, pygame.Color(0,0,0), (0,0,size[0],size[1]))

	pygame.draw.rect(window, pygame.Color(0,0,0), (0,0,size[0],size[1]))
	edge = 0
	for index in hue_order:
		colour = pygame.Color(*[int(c) for c in 255*freq_rgb[index]])
		amp = transformed[index]
		width = amp+1
		pygame.draw.rect(window, colour, (edge, 0, width, size[1]))
		edge += width
	"""
	for freq, amp in enumerate(transformed[1:], 1):
		pygame.draw.line(window,
			pygame.Color(*[int(c) for c in 255*freq_rgb[freq]]),
			(ffact*freq, 0), (ffact*freq, amp*7))"""

	#pygame.draw.rect(window, pygame.Color(*rgb), (0,0,size[0],size[1]))
	pygame.display.update()
	

	for event in pygame.event.get():
		if event.type == QUIT:
			pygame.quit()
			sys.exit(0)