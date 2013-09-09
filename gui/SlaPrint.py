from __future__ import unicode_literals
import sys, glob
import wx, os, signal
import subprocess
import threading, time

#Debug Globals
simulate_timer_ms=50

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
		
class PrintLoader(object):
	def threadLoad(self, path, filelist, start_index):
		self.running = True
		self.print_index = start_index
		self.path = path
		while self.print_index  < len(filelist)-1:
			self.current_file = filelist[self.print_index]
			self.PrintLayer()
			self.print_index  += 1	
		print "Thread has been stopped"

	def GetFileBeingPrinted(self):
		return self.path+"\\"+self.current_file
		
	def PrintLayer(self):
		#TODO Call png_scan logic
		print "Printing "+self.current_file+" ... "
		
		#TODO Move Z Axis
		time.sleep(1)
		
	def killThread(self):
		self.running = False
		
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
		self.panel = wx.Panel(self, -1)	
		self.imagePreviewPanel = wx.Panel(self, -1)
		self.PhotoMaxSize = 350
		img = wx.EmptyImage(self.PhotoMaxSize,self.PhotoMaxSize)
		self.imageCtrl = wx.StaticBitmap(self.imagePreviewPanel, wx.ID_ANY, 
										 wx.BitmapFromImage(img))
		self.currentImagePath=""
		self.imagePreviewPanel.SetBackgroundColour(wx.BLACK)
		buttonPanel = wx.Panel(self, -1 )
		consolePanel = wx.Panel(self, -1 )
		connectPanel = wx.Panel(self, -1 )
		menubar = wx.MenuBar()
		file = wx.Menu()
		file.Append(101, '&quit', 'Quit application')
	#	menubar.Append(file, '&File')
	
		self.connectToLaserSharkButton = wx.BitmapButton(buttonPanel, -1, scale_bitmap(wx.Bitmap('icons/connect-button.png'), 32, 32))
		self.disconnectFromLaserSharkButton	 = wx.BitmapButton(buttonPanel, -1, scale_bitmap(wx.Bitmap('icons/disconnect-button.png'), 32, 32))
		self.selectFileToPrintButton  = wx.BitmapButton(buttonPanel, -1, scale_bitmap(wx.Bitmap('icons/browse-button.png'), 32, 32))
		
		self.printButton  = wx.BitmapButton(buttonPanel, -1, scale_bitmap(wx.Bitmap('icons/print-button.png'), 32, 32))
		self.simulateButton	 = wx.BitmapButton(buttonPanel, -1, scale_bitmap(wx.Bitmap('icons/simulate-button.png'), 32, 32))
		self.pauseButton	 = wx.BitmapButton(buttonPanel, -1, scale_bitmap(wx.Bitmap('icons/pause-button.png'), 32, 32))
		self.homeZButton  = wx.BitmapButton(buttonPanel, -1, scale_bitmap(wx.Bitmap('icons/home-z-button.png'), 32, 32))
		self.ZUpButton	  = wx.BitmapButton(buttonPanel, -1, scale_bitmap(wx.Bitmap('icons/z-up-button.png'), 32, 32))
				
		self.Bind(wx.EVT_BUTTON, self.startLaserShark, self.connectToLaserSharkButton)
		self.Bind(wx.EVT_BUTTON, self.stopLaserShark, self.disconnectFromLaserSharkButton)
		self.Bind(wx.EVT_BUTTON, self.selectFileToPrint, self.selectFileToPrintButton)
		self.Bind(wx.EVT_BUTTON, self.printClicked, self.printButton)
		self.Bind(wx.EVT_BUTTON, self.simulateClicked, self.simulateButton)
		self.Bind(wx.EVT_BUTTON, self.pauseClicked, self.pauseButton)
		self.Bind(wx.EVT_BUTTON, self.HomeZ, self.homeZButton)
		self.Bind(wx.EVT_BUTTON, self.ZUp, self.ZUpButton)
		
		self.disconnectFromLaserSharkButton.Disable()
		self.pauseButton.Disable()
			
		log = wx.TextCtrl(consolePanel, wx.ID_ANY, size=(500,300),
						  style = wx.TE_MULTILINE|wx.TE_READONLY|wx.HSCROLL)
						  
		self.progress = wx.Slider(buttonPanel, -1, 0, 0, 100, size=(500, -1))
		vbox = wx.BoxSizer(wx.VERTICAL)
		hbox2 = wx.BoxSizer(wx.HORIZONTAL)
		hbox3 = wx.BoxSizer(wx.HORIZONTAL)
		
		hbox2.Add(self.connectToLaserSharkButton)
		hbox2.Add(self.disconnectFromLaserSharkButton, flag=wx.RIGHT, border=10)
		hbox2.Add(self.selectFileToPrintButton, flag=wx.RIGHT, border=20)
		hbox2.Add(self.printButton, flag=wx.RIGHT, border=5)
		hbox2.Add(self.simulateButton)
		hbox2.Add(self.pauseButton)
		hbox2.Add(self.homeZButton, flag=wx.LEFT, border=20)
		hbox2.Add(self.ZUpButton)
		
		vbox.Add(hbox3, 1, wx.EXPAND)
		vbox.Add(hbox2, 1, wx.EXPAND)
		buttonPanel.SetSizer(vbox)
		connectPanel.SetSizer(vbox)
		sizer = wx.BoxSizer(wx.VERTICAL)
		
		self.rescanbtn=wx.Button(connectPanel,-1,"Scan",size=(100,32))
		self.rescanbtn.SetToolTip(wx.ToolTip("Communication Settings\nClick to rescan ports"))
		self.rescanbtn.Bind(wx.EVT_BUTTON,self.rescanports)
		self.port=""
		hbox3.Add(self.rescanbtn,0,wx.TOP|wx.LEFT,0)
		self.serialport = wx.ComboBox(connectPanel, -1,
				choices=self.scanserial(),
				style=wx.CB_DROPDOWN, size=(100, 25))
		self.serialport.SetToolTip(wx.ToolTip("Select Port Printer is connected to"))
		self.rescanports()
		hbox3.Add(self.serialport)
		hbox3.Add(wx.StaticText(connectPanel,-1,"@"),0,wx.RIGHT|wx.ALIGN_CENTER,0)
		self.baud = wx.ComboBox(connectPanel, -1,
				choices=["2400", "9600", "19200", "38400", "57600", "115200", "250000"],
				style=wx.CB_DROPDOWN,  size=(100, 25))
		self.baud.SetToolTip(wx.ToolTip("Select Baud rate for printer communication"))
		try:
			self.baud.SetValue("115200")
		except:
			pass
		hbox3.Add(self.baud)
		hbox3.Add((500, -1), 1, flag=wx.EXPAND | wx.TOP | wx.ALIGN_RIGHT)
		
		sizer.Add(connectPanel, flag=wx.EXPAND)
		sizer.Add(self.imagePreviewPanel, 1, flag=wx.EXPAND)
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
		
		self.print_loaded = False
		self.connected = False
		
		global simulate_timer_ms
		self.simulate_timer_ms=simulate_timer_ms

	def scanserial(self):
		"""scan for available ports. return a list of device names."""
		baselist=[]
		if os.name=="nt":
			try:
				key=_winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE,"HARDWARE\\DEVICEMAP\\SERIALCOMM")
				i=0
				while(1):
					baselist+=[_winreg.EnumValue(key,i)[1]]
					i+=1
			except:
				pass
		return baselist+glob.glob('/dev/ttyUSB*') + glob.glob('/dev/ttyACM*') +glob.glob("/dev/tty.*")+glob.glob("/dev/cu.*")+glob.glob("/dev/rfcomm*")

	def rescanports(self,event=None):
		scan=self.scanserial()
		portslist=list(scan)
		if self.port != "" and self.port not in portslist:
			portslist += [self.port]
			self.serialport.Clear()
			self.serialport.AppendItems(portslist)
		try:
			if os.path.exists(self.port) or self.port in scan:
				self.serialport.SetValue(self.port)
			elif len(portslist)>0:
				self.serialport.SetValue(portslist[0])
		except:
			pass


	def on_timer(self, event):
		self.DoLoadNextFile()
		
	def on_print_timer(self, event):
		self.currentImagePath = self.loadPrintThread.GetFileBeingPrinted()
		self.DoLoadNextFile()
		
	def disconnect(self):
		self.connectToLaserSharkButton.Enable()
		self.disconnectFromLaserSharkButton.Disable()
		self.loadLaserSharkThread.killThread()
		self.loadPrintThread.killThread()
		
	def startLaserShark(self, event): 
		print "Connecting to OpenSL Printer..."
		self.connected = True
		self.disconnectFromLaserSharkButton.Enable()
		self.connectToLaserSharkButton.Disable()
		self.loadLaserSharkThread = Loader()
		self.laserSharkThread = threading.Thread(target=self.loadLaserSharkThread.threadLoad, args=("notepad %s" % "filename.txt", ))
		self.laserSharkThread.start()
		self.loadPrintThread = PrintLoader()
		
	def stopLaserShark(self, event): 
		print "Disconnecting from OpenSL Printer..."
		self.disconnect()
		
	def printClicked(self, event):
		if not self.connected:
			print "Connect to Printer first!"
			return
			
		if self.print_loaded:
			print "Starting Print..."
			path, pFile = os.path.split(self.currentImagePath)
			self.printThread = threading.Thread(target=self.loadPrintThread.threadLoad, args=(path, self.GetFileList(path), self.GetFileIndex(self.GetFileList(path), pFile), ))
			self.printThread.start()
			
			TIMER_ID = 101	# pick a number
			self.timer = wx.Timer(self.panel, TIMER_ID)	# message will be sent to the panel
			wx.EVT_TIMER(self.panel, TIMER_ID, self.on_print_timer)  # call the on_timer function
			self.timer.Start(self.simulate_timer_ms)  # x100 milliseconds
		else:
			print "Load a print first!"
		
	def simulateClicked(self, event):
		if self.print_loaded:
			self.simulateButton.Disable()
			self.pauseButton.Enable()
			print "Simulating Print..."
			TIMER_ID = 100	# pick a number
			self.timer = wx.Timer(self.panel, TIMER_ID)	# message will be sent to the panel
			wx.EVT_TIMER(self.panel, TIMER_ID, self.on_timer)  # call the on_timer function
			self.timer.Start(self.simulate_timer_ms)  # x100 milliseconds
		else:
			print "Load a print first!"
		
	def pauseClicked(self, event):
		if self.print_loaded:
			self.pauseButton.Disable()
			self.simulateButton.Enable()
			print "Stopping Print"
			self.timer.Stop()
		
		
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
			self.print_loaded = True
		dialog.Destroy() 
		self.LoadFilePreview()
		
	def LoadNextFile(self,e):
		self.DoLoadNextFile()
	
	def GetFileList(self, path):
		extension = ".png"
		list_of_files = [file for file in os.listdir(path) if file.lower().endswith(extension)]
		return list_of_files
		
	def GetFileIndex(self, list_of_files, filename):
		return list_of_files.index(unicode(filename))
		
	def DoLoadNextFile(self):
		"""
		Load next file for print
		"""
		path, pFile = os.path.split(self.currentImagePath)
		list_of_files = self.GetFileList(path)
		if self.GetFileIndex(list_of_files, pFile) < (len(list_of_files)-1) :
			self.currentImagePath = path + "\\"+ list_of_files[self.GetFileIndex(list_of_files, pFile) + 1]
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