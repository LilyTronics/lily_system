"""
Main view of the application
"""

import wx


class ViewMain(wx.MDIParentFrame):

    ID_MENU_EXIT = 100
    ID_TREE = 200

    _GAP = 5
    _MIN_WINDOW_SIZE = (1000, 600)
    _TREE_WIDTH = 300

    def __init__(self, title):
        super().__init__(None, wx.ID_ANY, title)

        self._create_menu()
        self._create_tree()

        # panel = wx.Panel(self)
        # box = wx.BoxSizer(wx.HORIZONTAL)
        # box.Add(self._create_tree(panel), 0, wx.EXPAND | wx.ALL, self._GAP)
        # box.Add(self._create_notebook(panel), 1, wx.EXPAND | wx.ALL, self._GAP)
        # panel.SetSizer(box)
        self.SetInitialSize(self._MIN_WINDOW_SIZE)

        self.Bind(wx.EVT_MENU, self._on_menu_exit, id=self.ID_MENU_EXIT)
        self.Bind(wx.EVT_SIZE, self._on_window_resize)

    def _create_menu(self):
        menu = wx.Menu()
        menu.Append(self.ID_MENU_EXIT, "E&xit")
        menubar = wx.MenuBar()
        menubar.Append(menu, "&File")
        self.SetMenuBar(menubar)

    def _create_tree(self):
        tb = self.CreateToolBar(style=wx.TB_VERTICAL)
        tb.SetToolBitmapSize((self._TREE_WIDTH, -1))

        self._tree = wx.TreeCtrl(tb, self.ID_TREE, pos=(self._GAP, self._GAP))
        self._tree.AddRoot("Lily System\u2122")
        tb.AddControl(self._tree)

    def _create_notebook(self, parent):
        self._notebook = wx.Notebook(parent)
        return self._notebook

    def _find_item(self, item_id, parent):
        item, cookie = self._tree.GetFirstChild(parent)
        while item.IsOk():
            if self._tree.GetItemText(item) == item_id:
                return item
            item, cookie = self._tree.GetNextChild(self._tree.GetRootItem(), cookie)

    def _on_menu_exit(self, event):
        self.Close()
        event.Skip()

    def _on_window_resize(self, event):
        tb_width, tb_height = self.GetToolBar().GetSize()
        self._tree.SetSize((tb_width - (2 * self._GAP), tb_height - (2 * self._GAP)))
        event.Skip()

    def add_rack(self, rack_id):
        root = self._tree.GetRootItem()
        if self._find_item(rack_id, root) is None:
            self._tree.AppendItem(root, rack_id)
            self._tree.ExpandAll()

    def add_module(self, rack_id, module_id, location):
        root = self._tree.GetRootItem()
        rack_item = self._find_item(rack_id, root)
        if rack_item is not None:
            if self._find_item(module_id, rack_item) is None:
                item = self._tree.AppendItem(rack_item, module_id, data=location)
                # item.location = location
        self._tree.ExpandAll()

    def get_item_data(self, item):
        return self._tree.GetItemData(item)


if __name__ == "__main__":

    def _on_tree_item_activate(event):
        print(f.get_item_data(event.GetItem()))


    app = wx.App(redirect=False)

    f = ViewMain("MainView Test")
    f.Bind(wx.EVT_TREE_ITEM_ACTIVATED, _on_tree_item_activate, id=f.ID_TREE)
    f.Show()
    # Populate tree with some racks and modules
    for i in range(3):
        _rack_id = f"Rack [COM{i + 1}]"
        f.add_rack(_rack_id)
        for j in range(5):
            _module_id = f"{j + 1} - Module {j + 1}"
            f.add_module(_rack_id, _module_id, (f"COM{i + 1}", j + 1))
    # Try to add an existing one
    f.add_rack("Rack [COM2]")
    f.add_module("Rack [COM1]", "4 - Module 4", ("COM1", 4))
    # Try to add a module for a not existing rack
    f.add_module("Rack [COM9]", "4 - Module 4", ("COM9", 4))

    app.MainLoop()
