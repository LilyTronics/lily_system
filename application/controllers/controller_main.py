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

    def _on_lily_system_event(self, racks):
        for key in sorted(racks):
            self._view.add_rack(key)
            for module in sorted(racks[key], key=lambda m: m["slot"]):
                self._view.add_module(key, f"{module["slot"]} - {module["name"]}")


if __name__ == "__main__":

    app = wx.App(redirect=False)
    ControllerMain("ControllerMain Test")
    app.MainLoop()
