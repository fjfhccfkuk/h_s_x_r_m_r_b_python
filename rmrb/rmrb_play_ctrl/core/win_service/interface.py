#!/usr/bin/python


class InterfaceWinCtrl(object):
    def __init__(self):
        pass

    def start_browser(self):
        raise Exception("InterfaceWinctrl should be override by subclass")

    def restart_browser(self):
        raise Exception("InterfaceWinctrl should be override by subclass")

