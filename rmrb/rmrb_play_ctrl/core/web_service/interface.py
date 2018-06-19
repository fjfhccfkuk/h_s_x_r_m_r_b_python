#!/usr/bin/python


class InterfaceWebSer(object):
    def __init__(self):
        pass

    def send_media(self, abspath):
        raise Exception("InterfaceWinctrl should be override by subclass")

