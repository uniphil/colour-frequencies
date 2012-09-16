import sys
import numpy as np
import jack
from pylab import plot, show, draw, ion, xlim, ylim, xscale, bar, array, \
	log2, nan, average

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

freq_rgb = array([hue_to_rgb((log2(F) - log2(440)) % 1)  for F in freqs])

capture = np.zeros((1, buff), 'f')
dummy = np.zeros((0,0), 'f')

"""ion()
bars = bar(freqs, range(buff/2))
xscale('log')
ylim((0,1))"""

import pygame
from pygame.locals import *
pygame.init()
size = (640, 380)
window = pygame.display.set_mode(size)

class Rolling(list):
	def __init__(self, size, placeholder=0):
		self.size = size
		self.index = 0
		self.extend(placeholder for n in range(size))
	def push(self, item):
		self[self.index] = item
		self.index = (self.index + 1) % self.size

		
last3 = Rolling(1, [0,0,0])

while True:
	try:
		jack.process(dummy, capture)
	except jack.InputSyncError:
		print 'Input Sync'

	transformed = np.fft.rfft(capture[0][1:])
	rgbs = (transformed * freq_rgb.T)[:,1:]
	rgb = [average(col)*1024 for col in rgbs]
	#last3.push(rgb)
	#rgb = [average(c) for c in array(last3).T]
	rgb = [(int(c) if c < 256 else 255) if c >= 0 else 0 for c in rgb]

	last3.push(rgb)

	print rgb
	pygame.draw.rect(window, pygame.Color(*rgb), (0,0,size[0],size[1]))
	pygame.display.update()
	

	for event in pygame.event.get():
		if event.type == QUIT:
			pygame.quit()
			sys.exit(0)