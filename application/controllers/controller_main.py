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

        self._view.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self._on_tree_item_activate, id=self._view.ID_TREE)

        self._lily_system = LilySystem(self._on_lily_system_event)

    def _on_lily_system_event(self, racks):
        for rack in sorted(racks, key=lambda r: r["port"]):
            rack_id = f"Rack [{rack["port"]}]"
            self._view.add_rack(rack_id)
            for module in sorted(rack["modules"], key=lambda m: m["slot"]):
                module_id = f"{module["slot"]} - {module["name"]}"
                self._view.add_module(rack_id, module_id, (rack["port"], module["slot"]))

    def _on_tree_item_activate(self, event):
        location = self._view.get_item_data(event.GetItem())
        if location is not None:
            matches = list(filter(lambda r: r["port"] == location[0], self._lily_system.get_racks()))
            if len(matches) == 1:
                matches = list(filter(lambda m: m["slot"] == location[1], matches[0]["modules"]))
                print(location, matches)
        event.Skip()


if __name__ == "__main__":

    from models.simulator.simulators import Simulators

    Simulators.run()

    app = wx.App(redirect=False)
    ControllerMain("ControllerMain Test")
    app.MainLoop()
