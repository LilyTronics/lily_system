"""
Start the application
"""

import wx

from app_info import AppInfo
from controllers.controller_main import ControllerMain

app = wx.App(redirect=False)
ControllerMain(f"{AppInfo.NAME} V{AppInfo.VERSION}")
app.MainLoop()
