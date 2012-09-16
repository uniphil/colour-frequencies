import sys, time
from math import sin, pi
from itertools import cycle
import pygame
import pygame.gfxdraw
from numpy import array, fft, trapz

pygame.init()
size = (1024, 600)
display = pygame.display.set_mode(size)

def f(phase, period, samples):
    sample_range = xrange(phase, phase+samples+1)
    return array([sin(t/(period/ (2*pi))) for t in sample_range])


white = pygame.Color(255, 255, 255, 127)
light = pygame.Color(127, 127, 127, 127)
dark = pygame.Color(32, 32, 32, 127)
extra_light = pygame.Color(127, 127, 127, 32)
light_red = pygame.Color(255,127,127,127)
light_yellow = pygame.Color(255,255,127, 127)
light_green = pygame.Color(127,255,127, 64)

anim_rate = 35

phase = 0
#period = 256.0
period = 256.0
for phase in cycle(range(256)):
#for period in cycle(range(128, 1024)):

    # generate the wave under inspection
    phase, period, window = phase, period, 512
    wave = f(phase, period, size[0])

    # wave graph
    scale = 128
    top_text = 16
    top_font = pygame.font.Font(None, top_text)

    # clear the screen
    display.fill((0,0,0), (0, 0, size[0], size[1]))

    # write graph info
    text = top_font.render(
        'phase: {}    period: {}    freq: {}    window: {}'.format(
        phase, period, 1/period, window), True, light)
    display.blit(text, dest=(8, 0))

    # draw the wave grid
    pygame.gfxdraw.hline(display, 0, size[0], scale+top_text, light)
    for sect in range(0, size[0], 8):
        pygame.gfxdraw.hline(display, sect, sect+4, top_text, light)
        pygame.gfxdraw.hline(display, sect, sect+4, scale*2+top_text, light)

    # draw the wave
    def valiaspx(surface, x, y, colour):
        colour = pygame.Color(*colour)
        fract = y - int(y)
        colour.a = int(255*fract)
        pygame.gfxdraw.pixel(surface, x, int(y)+1, colour)
        colour.a = int(255*(1-fract))
        pygame.gfxdraw.pixel(surface, x, int(y), colour)
    for frame, amp in [e for e in enumerate(scale * wave)][:window+1]:
        valiaspx(display, frame, amp+scale+top_text, light_yellow)

    # mask the wave
    mask = (window, top_text, size[0]-window, scale*2+1)
    #pygame.gfxdraw.box(display, mask, dark)
    for sect in range(top_text, top_text+scale*2+1, 4):
        pygame.gfxdraw.vline(display, window, sect,
            min([sect+1, top_text+scale*2]), light)



    mid_top = top_text + scale*2+1 + 32

    # compute the fft
    freqs = fft.fftfreq(window)
    f_amps = fft.rfft(wave[:window+1])
    f_scale = max(freqs) / size[0]
    a_scale = 0.45
    base = mid_top + scale
    
    # record some fft stats
    f_max = max(abs(freq) for freq in f_amps)
    f_int = trapz([abs(freq) for freq in f_amps], freqs[:window/2+1])
    text = top_font.render(
        'maximum: {0:.2f}    integrated: {1:.6f}'.format(f_max, f_int),
            True, light)
    display.blit(text, dest=(8, mid_top-16))
    pygame.gfxdraw.hline(display, 232, int(232+f_int*1200), mid_top-8,
        light_yellow)
    pygame.gfxdraw.vline(display, int(232+f_int*1200), mid_top-4, mid_top-12,
        light_yellow)

    # draw the fft grid
    pygame.gfxdraw.hline(display, 0, size[0], base, light)
    for sect in range(0, size[0], 8):
        pygame.gfxdraw.hline(display, sect, sect+4, base-scale, light)
        pygame.gfxdraw.hline(display, sect, sect+4, base+scale, light)

    # draw the fft
    for index, a in enumerate(f_amps):
        x = int(round(freqs[index] / f_scale))
        h = int(round(a_scale*abs(a)))
        real = int(round(a_scale*a.real))
        imag = int(round(a_scale*a.imag))
        pygame.gfxdraw.vline(display, x, base, base-h, light_yellow)
        pygame.gfxdraw.vline(display, x-1, base, base-real, light_red)
        pygame.gfxdraw.vline(display, x+1, base, base-imag, light_green)

    pygame.display.update()

    time.sleep(min(0, abs(1.0/anim_rate-0.1)))




