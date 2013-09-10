import sys, glob
import wx, os, signal
import subprocess
import threading, time

import PngScan

class PrintLoader(object):
	def threadLoad(self, path, filelist, start_index, previewMode, laserMode, laserPower, xScale, yScale, simZ, tilt, move_speed, layer_height, printerSerial):
		self.running = True
		self.print_index = start_index
		self.path = path
		self.pngScanner = PngScan.PngScan()
		self.vertical=False
		self.laserMode = laserMode
		self.previewMode = previewMode
		self.laserPower = float(laserPower)
		self.xscale = float(xScale)/100.0
		self.yscale = float(yScale)/100.0
		self.simulate = simZ
		self.tilt = tilt
		self.tilt_speed = move_speed
		self.layer_move=float(self.tilt)-float(layer_height)
		self.printerSerial = printerSerial
		while self.print_index  < len(filelist)-1:
			self.current_file = filelist[self.print_index]
			self.PrintLayer(self.laserMode, self.previewMode, self.laserPower, self.xscale, self.yscale)
			self.print_index  += 1	
			if self.vertical:
				self.vertical = False
			else:
				self.vertical = True
		self.killThread()
		
	def GetFileBeingPrinted(self):
		return self.path+"/"+self.current_file
		
	def PrintLayer(self, laser, preview, laserPower, xscale, yscale):
		print "Printing "+self.current_file+" ... "
		self.pngScanner.ScanLayer(self.path+"/"+self.current_file, self.vertical, preview, laser, laserPower, xscale, yscale)
		print "Moving Z Axis"
		self.printerSerial.send("G91", self.simulate) # Relative Pos
		self.printerSerial.send("G1 L"+str(self.tilt)+" F"+str(self.tilt_speed), self.simulate) #Left side up 5mm
		self.printerSerial.send("G4 P500", self.simulate) # Wait 500 ms
		self.printerSerial.send("G1 R"+str(self.tilt)+" F"+str(self.tilt_speed), self.simulate) # Right side up 5 mm
		self.printerSerial.send("G4 P500", self.simulate) # Wait 500 ms
		self.printerSerial.send("G1 Z-"+str(self.layer_move)+" F"+str(self.tilt_speed), self.simulate) # Z down 5 mm
		self.printerSerial.send("G4 P1000", self.simulate) # Wait 1 Second
		self.printerSerial.send("M84", self.simulate) # Motors Off
		time.sleep(5) #Sleep for 10 seconds
	
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
		