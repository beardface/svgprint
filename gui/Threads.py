import sys, glob
import wx, os, signal
import subprocess
import threading, time

import PngScan

#Scan Settings
XSCALE=1.0
YSCALE=1.0
LASER_POWER=1000

class PrintLoader(object):
	def threadLoad(self, path, filelist, start_index, previewMode, laserMode):
		self.running = True
		self.print_index = start_index
		self.path = path
		self.pngScanner = PngScan.PngScan()
		self.vertical=False
		self.laserMode = laserMode
		self.previewMode = previewMode
		while self.print_index  < len(filelist)-1:
			self.current_file = filelist[self.print_index]
			self.PrintLayer(self.laserMode, self.previewMode)
			self.print_index  += 1	
			if self.vertical:
				self.vertical = False
			else:
				self.vertical = True
		self.killThread()
		
	def GetFileBeingPrinted(self):
		return self.path+"/"+self.current_file
		
	def PrintLayer(self, laser, preview):
		print "Printing "+self.current_file+" ... "
		global XSCALE
		global YSCALE
		global LASER_POWER
		self.pngScanner.ScanLayer(self.path+"/"+self.current_file, self.vertical, preview, laser, LASER_POWER, XSCALE, YSCALE)
	
	def SetLaserMode(self, b):
		self.laserMode = b
	
	def SetPreviewMode(self, b):
		self.previewMode = b
		
	def killThread(self):
		self.running = False
	
	def IsPrintComplete(self):
		return not self.running
		
class Loader(object):
	def threadLoad(self, load_cmd):
		self.run = subprocess.Popen(load_cmd, shell=True, stdout=subprocess.PIPE)
		print
		self.running = True
		self.pid = self.run.pid
		while self.running:
			line = self.run.stdout.readline()						 
			#wx.Yield()
			if line.strip() == "":
				pass
			else:
				print line.strip()
			if not line: break
		self.run.wait()
		print "Thread has been stopped"

	def killThread(self):
		print "Waiting to kill "+str(self.pid)+" ..."
		try:
			self.run.kill()
			os.killpg(self.pid, signal.SIGTERM)
		except: 
			print "Process "+str(self.pid)+" Not Found."
		self.running = False
		