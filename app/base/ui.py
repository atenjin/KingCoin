#!/usr/bin/env python  
# -*- coding: utf-8 -*-

import wx

from app import context as ctx


def mainframe_repaint():
    if ctx.frameMain:
        print ("MainFrameRepaint()")
        ctx.frameMain.Refresh()
        ctx.frameMain.GetEventHandler().AddPendingEvent(wx.PaintEvent())


def main():
    pass


if __name__ == '__main__':
    main()
