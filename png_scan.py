from PIL import Image
from optparse import OptionParser
import sys

#import and init pygame
import pygame
from pygame import gfxdraw

import pylase as ol

from math import pi

def IsPixelOn(pixel):
    if pixel[0] != 0:
        return True
    else:
        return False

def PixelCoordToGalvoCoord(x, y, w, h):
    sX=(float(x)/float(w))*2.0 - 1.0
    sY=(float(y)/float(h))*2.0 - 1.0
    return [sX, sY]

def GalvoCoordToPixelCoord(point, w, h):
    sX=((point[0]+1.0)/2.0)*w
    sY=((point[1]+1.0)/2.0)*h
    return [sX, sY]
               
def scanPixel(pixel, x, y, preview, laser, w,h):
    sX=(float(x)/float(w))*2.0 - 1.0
    sY=(float(y)/float(h))*2.0 - 1.0
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

parser.add_option("-l", "--laser", action="store_true", dest="laser", default=False,
                  help="laser")

parser.add_option("-w", "--power", dest="power", default=1000, help="Laser Power (20-1000)")

parser.add_option("-x", "--xscale", dest="xscale", default=0.999, help="X Scale for Laser Scan (0.001-0.999)")

parser.add_option("-y", "--yscale", dest="yscale", default=0.999, help="Y Scale for Laser Scan (0.001-0.999)")

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
    rangeA = range(width)
    rangeB = range(height)
else:
    rangeA = range(height)
    rangeB = range(width)
    
for dirA in rangeA:
    scanline=[]
    scanning_on = False
    pixel_on =[0, 0]
    if options.laser:
        ol.loadIdentity()
        ol.scale((float(options.xscale), float(options.yscale)))
        x = 0
        y = 0
    for dirB in rangeB:
        if options.vertical:
            x = dirA
            y = dirB
        else:
            x = dirB
            y = dirA
        if IsPixelOn(pixels[x, y]):
            if scanning_on == False:
                pixel_on = PixelCoordToGalvoCoord(x, y, width, height)
                scanning_on = True
        else:
            if scanning_on:
                scanline.append([pixel_on, PixelCoordToGalvoCoord(x, y, width, height)])
                scanning_on = False
    if scanning_on:
        scanline.append([pixel_on, PixelCoordToGalvoCoord(x, y, width, height)])
        scanning_on = False
    for s in scanline:
        if options.preview:
            pygame.draw.line(window, (255, 255, 255), GalvoCoordToPixelCoord(s[0], width, height), GalvoCoordToPixelCoord(s[1], width, height))
        if options.laser:
            ol.line((s[0][0],s[0][1]), (s[1][0],s[1][1]), ol.C_WHITE)
    if options.preview:
        pygame.display.flip()
    if options.laser:
        ol.renderFrame(int(options.power))

print options.svgfile,
print " Height:",
print height,
print " Width:",
print width

