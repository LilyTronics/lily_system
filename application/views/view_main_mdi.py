"""

"""

import wx


class ViewMainMdi(wx.MDIParentFrame):

    def __init__(self):
        super().__init__(None)

        menu = wx.Menu()
        menu.Append(1, "&New Window")
        menu.AppendSeparator()
        menu.Append(2, "E&xit")
        menubar = wx.MenuBar()
        menubar.Append(menu, "&File")
        self.SetMenuBar(menubar)

        self.Bind(wx.EVT_MENU, self.OnNewWindow, id=1)

        tb = self.CreateToolBar(style=wx.TB_VERTICAL)
        print(tb)
        tb.SetToolBitmapSize((300,-1))
        self._tree = wx.TreeCtrl(tb, size=(300, 200), pos=(5,5))
        tb.AddControl(self._tree)


    def OnNewWindow(self, evt):
        win = wx.MDIChildFrame(self, -1, "Child Window")
        win.Show(True)


if __name__ == "__main__":

    app = wx.App(redirect=False)

    f = ViewMainMdi()
    f.Show()

    app.MainLoop()
