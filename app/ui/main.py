#!/usr/bin/env python  
# -*- coding: utf-8 -*-

import wx
import traceback
from .mainframe import MainFrame

from app import context as ctx
from app.net import action as netaction
from app.net import nodeaction
from app.block import action as blkaction


class App(object):
    @staticmethod
    def run():
        app = MyApp(True)  # Create a new app, redirect stdout/stderr to a window.
        app.Init()
        frame = MainFrame(None)
        frame.Show(True)

        if not nodeaction.start_node():
            wx.MessageBox("start node failed!")

        if ctx.fGenerateCoins:
            frame.MinerThread(True)
        app.MainLoop()

    pass


class MyApp(wx.App):
    def Init(self):
        try:
            self.OnInit2()
        except Exception, e:
            print ("init error!")
            print (e)
            traceback.print_exc()
            wx.MessageBox(e.message + "\n" + traceback.format_exc())
        return False

    def OnInit2(self):
        # load data        if not netaction.load_addresses():

        print ("Loading addresses...")
        err = ''
        if not netaction.load_addresses():
            err += "Error loading addr.dat      \n"

        print ("Loading wallet...")
        if not blkaction.load_wallet():
            err += "Error loading wallet.dat      \n"

        print("Loading block index...")
        if not blkaction.load_blockindex():
            err += "Error loading blkindex.dat      \n"

        print ("Done loading")
        if err:
            print err

        # Add wallet transactions that aren't already in a block to mapTransactions
        blkaction.reaccept_wallet_txs()

        pass

    pass


def main():
    pass


if __name__ == '__main__':
    main()
