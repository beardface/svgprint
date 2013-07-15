from PIL import Image
from optparse import OptionParser
import sys

#import and init pygame
import pygame
from pygame import gfxdraw

def scanPixel(pixel, x, y, preview):
    if pixel[0] != 255:
        if preview:
            pygame.draw.line(window, (255, 255, 255), (x, y), (x, y))
            pygame.display.flip() 

parser = OptionParser()
parser.add_option("-f", "--file", dest="svgfile", help="SVG Layer File to Print")
parser.add_option("-v", "--vertical", action="store_true", dest="vertical", default=False,
                  help="Scan vertically")
parser.add_option("-p", "--preview", action="store_true", dest="preview", default=False,
                  help="Preview Scan")


(options, args) = parser.parse_args()

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
        for y in range(height):
            scanPixel(pixels[x, y], x, y, options.preview)
else:
    for y in range(height):
        for x in range(width):
            scanPixel(pixels[x, y], x, y, options.preview)

print options.svgfile,
print " Height:",
print height,
print " Width:",
print width