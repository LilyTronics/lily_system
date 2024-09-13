"""
Main view of the application
"""

import wx


class ViewMain(wx.Frame):

    _GAP = 10
    _MIN_WINDOW_SIZE = (900, 600)

    def __init__(self, title):
        super().__init__(None, wx.ID_ANY, title)
        panel = wx.Panel(self)
        box = wx.BoxSizer(wx.HORIZONTAL)
        box.Add(self._create_tree(panel), 30, wx.EXPAND | wx.ALL, self._GAP)
        box.Add(self._create_notebook(panel), 70, wx.EXPAND | wx.ALL, self._GAP)
        panel.SetSizer(box)
        self.SetInitialSize(self._MIN_WINDOW_SIZE)

    def _create_tree(self, parent):
        self._tree = wx.TreeCtrl(parent)
        self._tree.AddRoot("Lily System\u2122")
        return self._tree

    def _create_notebook(self, parent):
        self._notebook = wx.Notebook(parent)
        return self._notebook

    def _find_item(self, item_id, parent):
        item, cookie = self._tree.GetFirstChild(parent)
        while item.IsOk():
            if self._tree.GetItemText(item) == item_id:
                return item
            item, cookie = self._tree.GetNextChild(self._tree.GetRootItem(), cookie)

    def add_rack(self, rack_id):
        root = self._tree.GetRootItem()
        if self._find_item(rack_id, root) is None:
            self._tree.AppendItem(root, rack_id)
            self._tree.ExpandAll()

    def add_module(self, rack_id, module_id):
        root = self._tree.GetRootItem()
        rack_item = self._find_item(rack_id, root)
        if rack_item is not None:
            if self._find_item(module_id, rack_item) is None:
                self._tree.AppendItem(rack_item, module_id)
        self._tree.ExpandAll()


if __name__ == "__main__":

    app = wx.App(redirect=False)
    f = ViewMain("MainView Test")
    f.Show()
    # Populate tree with some racks and modules
    for i in range(3):
        _rack_id = f"Rack (COM{i + 1})"
        f.add_rack(_rack_id)
        for j in range(5):
            _module_id = f"{j + 1} - Module {j + 1}"
            f.add_module(_rack_id, _module_id)
    # Try to add an existing one
    f.add_rack("Rack (COM2)")
    f.add_module("Rack (COM1)", "4 - Module 4")
    # Try to add a module for a not existing rack
    f.add_module("Rack (COM9)", "4 - Module 4")
    app.MainLoop()
