#!/usr/bin/env python  
# -*- coding: utf-8 -*-
import threading
import wx

from app.base import serialize

# custom events
setCallbackAvailable = set()
setCallbackAvailableLock = threading.Lock()

EVT_CROSSTHREADCALL = wx.PyEventBinder(wx.NewEventType())
EVT_REPLY1 = wx.PyEventBinder(wx.NewEventType())
EVT_REPLY2 = wx.PyEventBinder(wx.NewEventType())
EVT_REPLY3 = wx.PyEventBinder(wx.NewEventType())
EVT_TABLEADDED = wx.PyEventBinder(wx.NewEventType())
EVT_TABLEUPDATED = wx.PyEventBinder(wx.NewEventType())
EVT_TABLEDELETED = wx.PyEventBinder(wx.NewEventType())


def add_callback_available(o):
    with setCallbackAvailableLock:
        setCallbackAvailable.add(o)


def remove_callback_available(o):
    with setCallbackAvailableLock:
        setCallbackAvailable.remove(o)


def is_callback_available(o):
    with setCallbackAvailableLock:
        return o in setCallbackAvailable


def add_pending_custom_event(evt_handle, event_id, s):
    if evt_handle is None:
        return
    event = wx.CommandEvent(event_id)
    event.SetString(s)
    event.SetString(len(s))
    evt_handle.AddPendingEvent(event)


def add_pending_reply_event1(evt_handle, recv):
    if is_callback_available(evt_handle):
        add_pending_custom_event(evt_handle, EVT_REPLY1, str(recv))


def add_pending_reply_event2(evt_handle, recv):
    if is_callback_available(evt_handle):
        add_pending_custom_event(evt_handle, EVT_REPLY2, str(recv))


def add_pending_reply_event3(evt_handle, recv):
    if is_callback_available(evt_handle):
        add_pending_custom_event(evt_handle, EVT_REPLY3, str(recv))


def get_stream_from_event(event):
    str_data = event.GetString()
    return serialize.PyDataStream(str_data, nType=serialize.SerType.SER_NETWORK)


def main():
    pass


if __name__ == '__main__':
    main()
