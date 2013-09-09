from __future__ import unicode_literals
import sys
import wx, os, signal
import subprocess
import threading

#Configuration Globals
serial_port=""
serial_baud=115200

#Debug Globals
debug = True
simulate_timer_ms=100

def scale_bitmap(bitmap, width, height):
	image = wx.ImageFromBitmap(bitmap)
	image = image.Scale(width, height, wx.IMAGE_QUALITY_HIGH)
	result = wx.BitmapFromImage(image)
	return result
		
class RedirectText(object):
	def __init__(self,aWxTextCtrl):
		self.out=aWxTextCtrl
 
	def write(self,string):
		self.out.WriteText(string)
		
class Loader(object):
	def threadLoad(self, load_cmd):
		run = subprocess.Popen(load_cmd, shell=True, stdout=subprocess.PIPE)
		print
		self.running = True
		self.pid = run.pid
		while self.running:
			line = run.stdout.readline()						 
			wx.Yield()
			if line.strip() == "":
				pass
			else:
				print line.strip()
			if not line: break
		run.wait()
		print "Thread has been stopped"

	def killThread(self):
		print "Waiting to kill "+str(self.pid)+" ..."
		os.kill(self.pid, signal.SIGTERM)
		self.running = False
		
class SlaPrintMainForm(wx.Frame):
 
	def __init__(self):
		wx.Frame.__init__(self, None, wx.ID_ANY, "OpenSL SLA Print Control Panel", size=(500, 1000))
		panel = wx.Panel(self, -1)	
		self.imagePreviewPanel = wx.Panel(self, -1)
		self.PhotoMaxSize = 350
		img = wx.EmptyImage(self.PhotoMaxSize,self.PhotoMaxSize)
		self.imageCtrl = wx.StaticBitmap(self.imagePreviewPanel, wx.ID_ANY, 
										 wx.BitmapFromImage(img))
		self.currentImagePath=""
		self.imagePreviewPanel.SetBackgroundColour(wx.BLACK)
		buttonPanel = wx.Panel(self, -1 )
		consolePanel = wx.Panel(self, -1 )
		menubar = wx.MenuBar()
		file = wx.Menu()
		file.Append(101, '&quit', 'Quit application')
	#	menubar.Append(file, '&File')
		slider1 = wx.Slider(buttonPanel, -1, 0, 0, 1000)
		self.connectToLaserSharkButton = wx.BitmapButton(buttonPanel, -1, scale_bitmap(wx.Bitmap('icons/connect-button.png'), 32, 32))
		self.disconnectFromLaserSharkButton	 = wx.BitmapButton(buttonPanel, -1, scale_bitmap(wx.Bitmap('icons/disconnect-button.png'), 32, 32))
		self.selectFileToPrintButton  = wx.BitmapButton(buttonPanel, -1, scale_bitmap(wx.Bitmap('icons/browse-button.png'), 32, 32))
		
		self.printButton  = wx.BitmapButton(buttonPanel, -1, scale_bitmap(wx.Bitmap('icons/print-button.png'), 32, 32))
		self.homeZButton  = wx.BitmapButton(buttonPanel, -1, scale_bitmap(wx.Bitmap('icons/home-z-button.png'), 32, 32))
		self.ZUpButton    = wx.BitmapButton(buttonPanel, -1, scale_bitmap(wx.Bitmap('icons/z-up-button.png'), 32, 32))
				
		self.Bind(wx.EVT_BUTTON, self.startLaserShark, self.connectToLaserSharkButton)
		self.Bind(wx.EVT_BUTTON, self.stopLaserShark, self.disconnectFromLaserSharkButton)
		self.Bind(wx.EVT_BUTTON, self.selectFileToPrint, self.selectFileToPrintButton)
		self.Bind(wx.EVT_BUTTON, self.printClicked, self.printButton)
		self.Bind(wx.EVT_BUTTON, self.HomeZ, self.homeZButton)
		self.Bind(wx.EVT_BUTTON, self.ZUp, self.ZUpButton)
		
		self.disconnectFromLaserSharkButton.Disable()
		log = wx.TextCtrl(consolePanel, wx.ID_ANY, size=(500,300),
						  style = wx.TE_MULTILINE|wx.TE_READONLY|wx.HSCROLL)
						  
		self.progress = wx.Slider(buttonPanel, -1, 0, 0, 100, size=(500, -1))
		vbox = wx.BoxSizer(wx.VERTICAL)
		hbox1 = wx.BoxSizer(wx.HORIZONTAL)
		hbox2 = wx.BoxSizer(wx.HORIZONTAL)
		
		hbox2.Add(self.connectToLaserSharkButton, flag=wx.RIGHT, border=5)
		hbox2.Add(self.disconnectFromLaserSharkButton)
		hbox2.Add(self.selectFileToPrintButton)
		hbox2.Add(self.printButton)
		hbox2.Add(self.homeZButton)
		hbox2.Add(self.ZUpButton)
		
		hbox2.Add((150, -1), 1, flag=wx.EXPAND | wx.ALIGN_RIGHT)
		vbox.Add(hbox1, 1, wx.EXPAND | wx.BOTTOM, 10)
		vbox.Add(hbox2, 1, wx.EXPAND)
		buttonPanel.SetSizer(vbox)
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(self.imagePreviewPanel, 1, flag=wx.TOP|wx.EXPAND)
		sizer.Add(buttonPanel, flag=wx.EXPAND, border=10)
		sizer.Add(consolePanel, flag=wx.BOTTOM|wx.EXPAND, border=10)
		self.SetMinSize((350, 300))
		self.SetMenuBar(menubar)
		self.CreateStatusBar()
		self.SetSizer(sizer)
		self.Centre()
		
		# redirect text here
		redir=RedirectText(log)
		sys.stdout=redir
		
		global debug
		global simulate_timer_ms
		self.debug=debug
		self.simulate_timer_ms=simulate_timer_ms
		if self.debug:
			TIMER_ID = 100  # pick a number
			self.timer = wx.Timer(panel, TIMER_ID)  # message will be sent to the panel
			wx.EVT_TIMER(panel, TIMER_ID, self.on_timer)  # call the on_timer function

	def on_timer(self, event):
		self.DoLoadNextFile()

	def disconnect(self):
		self.connectToLaserSharkButton.Enable()
		self.disconnectFromLaserSharkButton.Disable()
		self.loadLaserSharkThread.killThread()
	
	def startLaserShark(self, event): 
		print "Connecting to OpenSL Printer..."
		self.disconnectFromLaserSharkButton.Enable()
		self.connectToLaserSharkButton.Disable()
		self.loadLaserSharkThread = Loader()
		self.laserSharkThread = threading.Thread(target=self.loadLaserSharkThread.threadLoad, args=("notepad %s" % "filename.txt", ))
		self.laserSharkThread.start()
		
	def stopLaserShark(self, event): 
		print "Disconnecting from OpenSL Printer..."
		self.disconnect()
		
	def printClicked(self, event):
		print "Starting Print..."
		if self.debug:
			self.timer.Start(self.simulate_timer_ms)  # x100 milliseconds
		
	def HomeZ(self, event): 
		print "Homing Z...."
		
	def ZUp(self, event): 
		print "Moving Z Up..."
	
	def LoadFilePreview(self):
		self.onView()
	
	def selectFileToPrint(self,e):
		""" 
		Browse for file
		"""
		wildcard = "PNG files (*.png)|*.png"
		dialog = wx.FileDialog(None, "Choose a file",
							   wildcard=wildcard,
							   style=wx.OPEN)
		if dialog.ShowModal() == wx.ID_OK:
			self.currentImagePath = dialog.GetPath()
		dialog.Destroy() 
		self.LoadFilePreview()
		
	def LoadNextFile(self,e):
		self.DoLoadNextFile()
			
	def DoLoadNextFile(self):
		"""
		Load next file for print
		"""
		path, pFile = os.path.split(self.currentImagePath)
		extension = ".png"
		list_of_files = [file for file in os.listdir(path) if file.lower().endswith(extension)]
		if list_of_files.index(unicode(pFile)) < (len(list_of_files)-1) :
			self.currentImagePath = path + "\\"+ list_of_files[list_of_files.index(unicode(pFile)) + 1]
			self.LoadFilePreview()
		else:
			print "Print Complete! Disconnecting."
			self.timer.Stop()
			self.disconnect()

	def onView(self):
		filepath = self.currentImagePath
		img = wx.Image(filepath, wx.BITMAP_TYPE_ANY)
		# scale the image, preserving the aspect ratio
		W = img.GetWidth()
		H = img.GetHeight()
		if W > H:
			NewW = self.PhotoMaxSize
			NewH = self.PhotoMaxSize * H / W
		else:
			NewH = self.PhotoMaxSize
			NewW = self.PhotoMaxSize * W / H
		img = img.Scale(NewW,NewH)
 
		self.imageCtrl.SetBitmap(wx.BitmapFromImage(img))
		self.imagePreviewPanel.Refresh()

# Run the program
if __name__ == "__main__":
	app = wx.PySimpleApp()
	frame = SlaPrintMainForm().Show()
	app.MainLoop()