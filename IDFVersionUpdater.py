import wx

from IDFVersionUpdater.IDFVersionUpdater import VersionUpdaterWindow, doing_restart

# we will keep the form in a loop to handle requested restarts (language change, etc.)
running = True
app = wx.App(False)
while running:
    main_window = VersionUpdaterWindow()
    app.MainLoop()
    running = doing_restart()
