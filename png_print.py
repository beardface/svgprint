from PIL import Image
from optparse import OptionParser
import sys

#import and init pygame
import pygame
from pygame import gfxdraw
import pylase as ol

from math import pi

def scanPixel(pixel, x, y, preview, laser, w,h):
    sX=(float(x)/float(w))*2.0 - 1.0
    sY=(float(y)/float(h))*2.0 - 1.0
    #print sX," ",sY
    if pixel[0] != 0:
        if preview:
            pygame.draw.line(window, (255, 255, 255), (x, y), (x, y))
            pygame.display.flip()
        if laser:
            ol.dot((sX,sY),100,ol.C_WHITE)
            ol.renderFrame(100)             

parser = OptionParser()
parser.add_option("-f", "--file", dest="svgfile", help="SVG Layer File to Print")
parser.add_option("-v", "--vertical", action="store_true", dest="vertical", default=False,
                  help="Scan vertically")
parser.add_option("-p", "--preview", action="store_true", dest="preview", default=False,
                  help="Preview Scan")

parser.add_option("-l", "--lase", action="store_true", dest="laser", default=False,
                  help="Preview Scan")


(options, args) = parser.parse_args()

if options.laser:
    ol.init()

i = Image.open(options.svgfile)

pixels = i.load() # this is not a list
width, height = i.size

if options.preview:
    pygame.init() 
    #create the screen
    window = pygame.display.set_mode((width, height)) 

cur_pixel = pixels[0, 0]
print cur_pixel

if options.vertical:
    for x in range(width):
        if options.laser:
            ol.loadIdentity()
            ol.scale((0.999, 0.999))
        for y in range(height):
            scanPixel(pixels[x, y], x, y, options.preview, options.laser, width, height)
        if options.laser:
            ol.renderFrame(100)
else:
    for y in range(height):
        if options.laser:
            ol.loadIdentity()
            ol.scale((0.999, 0.999))
        for x in range(width):
            scanPixel(pixels[x, y], x, y, options.preview, options.laser, width, height)
        if options.laser:
            ol.renderFrame(100)

print options.svgfile,
print " Height:",
print height,
print " Width:",
print width