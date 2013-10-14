from PIL import Image
from optparse import OptionParser
import sys

import pygame, time
from pygame import gfxdraw

import pylase

from math import pi

def module_exists(module_name):
	try:
		__import__(module_name)
	except ImportError:
		print "Unable to Import Pylase (open lase)... this only works on linux.  Make sure you have pylase.so available!"
		return False
	else:
		return True

module_exists("pylase")
		
class PngScan(object):
	def IsPixelOn(self, pixel):
		try:
		   i = int(pixel)
		   if i == 0:
			  return False
		   else:
			  return True
		except ValueError:
		   if pixel[0] != 0:
			  return True
		   else:
			  return False
		except TypeError:
		   if pixel[0] != 0:
			  return True
		   else:
			  return False

	def PixelCoordToGalvoCoord(self, x, y, w, h):
		sX=(float(x)/float(w))*2.0 - 1.0
		sY=(float(y)/float(h))*2.0 - 1.0
		return [sX, sY]

	def GalvoCoordToPixelCoord(self, point, w, h):
		sX=((point[0]+1.0)/2.0)*w
		sY=((point[1]+1.0)/2.0)*h
		return [sX, sY]
				   
	def scanPixel(self, pixel, x, y, preview, laser, w,h):
		sX=(float(x)/float(w))*2.0 - 1.0
		sY=(float(y)/float(h))*2.0 - 1.0
		if pixel[0] != 0:
			if preview:
				pygame.draw.line(window, (255, 255, 255), (x, y), (x, y))
				pygame.display.flip()
			if laser:
				pylase.dot((sX,sY),100,pylase.C_WHITE)
				pylase.renderFrame(100)				
	
	def ScanLayer(self, png_file, vertical, preview, laser, power, xscale, yscale):
		#png_file = path of png file to scan
		#vertical = True | False (Scan Direction)
		#laser = True | False (Should we laser??)
		#power = Laser Power ( 1-1000)
		#xscale = (float) 0.0-1.0 Scale of X
		#yscale = (float) 0.0-1.0 Scale of X
		
		if laser:
			pylase.init()

		i = Image.open(png_file)

		pixels = i.load() # this is not a list
		width, height = i.size

		scaledWidth=int(float(xscale)*width)
		scaledHeight=int(float(yscale)*height)

		cur_pixel = pixels[0, 0]
		print cur_pixel

		if vertical:
			rangeA = range(width)
			rangeB = range(height)
		else:
			rangeA = range(height)
			rangeB = range(width)
		 
		print "Computing the scanlines...."
		scanlines=[]
		for dirA in rangeA:
			scanline=[]
			scanning_on = False
			pixel_on =[0, 0]
			if laser:
				x = 0
				y = 0
			for dirB in rangeB:
				if vertical:
					x = dirA
					y = dirB
				else:
					x = dirB
					y = dirA
				if self.IsPixelOn(pixels[x, y]):
					if scanning_on == False:
						pixel_on = self.PixelCoordToGalvoCoord(x, y, width, height)
						scanning_on = True
				else:
					if scanning_on:
						scanline.append([pixel_on, self.PixelCoordToGalvoCoord(x, y, width, height)])
						scanning_on = False
			if scanning_on:
				scanline.append([pixel_on, self.PixelCoordToGalvoCoord(x, y, width, height)])
				scanning_on = False
			if len(scanline) > 0:
				scanlines.append(scanline)
			scanlines.append(scanline)

		if preview:
			pygame.init() 
			#create the screen
			window = pygame.display.set_mode((scaledWidth, scaledHeight)) 

		print "Found ",len(scanlines),"non blank scan lines... scanning now..."
		for l in scanlines:
			if laser:
				pylase.loadIdentity()
				pylase.scale((float(xscale), float(yscale)))
			for s in l: 
				if preview:
					pygame.draw.line(window, (0, 255, 0), self.GalvoCoordToPixelCoord(s[0], scaledWidth, scaledHeight), self.GalvoCoordToPixelCoord(s[1], scaledWidth, scaledHeight))
				if laser:
					pylase.line((s[0][0],s[0][1]), (s[1][0],s[1][1]), pylase.C_WHITE)	
			if preview:
				pygame.display.flip()
			if laser:
				pylase.renderFrame(int(power))


