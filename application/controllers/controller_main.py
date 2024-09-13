"""
Main controller
"""

import wx

from models.lily_system import LilySystem
from views.view_main import ViewMain


class ControllerMain:

    def __init__(self, window_title):
        self._view = ViewMain(window_title)
        self._view.Show()
        self._lily_system = LilySystem(self._on_lily_system_event)

    def _on_lily_system_event(self, event_type):
        print(event_type)


if __name__ == "__main__":

    app = wx.App(redirect=False)
    ControllerMain("ControllerMain Test")
    app.MainLoop()
