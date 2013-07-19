import wx

class openprint(wx.Frame):
	def __init__(self, parent, id):
		wx.Frame.__init__(self,parent,id,'OpenPrint', size=(400,300))
		panel=wx.Panel(self)
		
		status=self.CreateStatusBar()
		menubar=wx.MenuBar()
		fileMenu=wx.Menu()
		helpMenu=wx.Menu()
		fileMenu.Append(wx.NewId(),"Quit","Good Bye...")
		helpMenu.Append(wx.NewId(),"Wiki","Visit the wiki for more help")
		menubar.Append(fileMenu, "File")
		menubar.Append(helpMenu, "Help")
		self.SetMenuBar(menubar)
		
if __name__=='__main__':
	app=wx.PySimpleApp()
	frame=openprint(parent=None,id=-1)
	frame.Show()
	app.MainLoop()