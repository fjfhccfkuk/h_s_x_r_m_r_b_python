#!/usr/bin/python

import gtk, wnck
import os, time
import struct

class WinTouch(object):
    def __init__(self, event_file):
        self.__cb_obj = None
        self.__des_file = event_file
        self.__fmt = 'LLHHI'
        self.__ev_type = 0x1
        self.__ev_key = 0x14a
        self.__ev_value = 0x0

    def register_listener(self, obj):
        print "register_listener called"
        self.__cb_obj = obj

    def __touch_event(self, raw):
        (t_se, t_use, type, key, value) = struct.unpack(self.__fmt, raw)
        if type == self.__ev_type and key == self.__ev_key and value == self.__ev_value:
            print "time_sec:%d" % t_se + " time_usec:%x" % t_use + " type:%x" % type + " key:%x" % key + " value:%x" % value
            if self.__cb_obj:
                print "touch _cb_obj not none"
                self.__cb_obj.on_screen_touched();
            else:
                print "touch _cb_obj none"

    def __get_sudo(self):
        import os, sys
        args = ['sudo', sys.executable] + sys.argv + [os.environ]
        # the next line replaces the currently-running process with the sudo
        os.execlpe('sudo', *args)

    def __check_sudo(self):
        import os, sys
        euid = os.geteuid()
        while euid != 0:
            self.__get_sudo()
            print 'win_touch __check_sudo obtain root user'
            time.sleep(2)
        print 'Running. Your euid is', euid

    def exec_touch_event(self):
        self.__check_sudo()
#        pass

        while not os.path.exists(self.__des_file):
            time.sleep(3)

        print 'win_touch, open file:', self.__des_file
        e_file = open(self.__des_file, 'rb')

        read_size = struct.calcsize(self.__fmt)

        while True:
            try:
                raw = e_file.read(read_size);
                if not raw:
                    continue
                self.__touch_event(raw)

            except Exception, e:
                print " excp:%s" % e.message

    def exec_fork(self):
        """ create pipe """
        pr, pw = os.pipe()

        """ for a process """
        subProcessId = os.fork()
        print " *************  do fork"
        if (subProcessId == 0):
            """ sub process do """
            fork_function()
        else:
            """ main process do """


class TouchListener(object):
    def on_screen_touched(self):
        raise Exception("TouchListener.onScreenTouch should be override by sub class")


def run_touch_service(win_ctrl):
    import threading

    winTouch = WinTouch('/dev/input/event6')
    winTouch.register_listener(win_ctrl)
    winTouchThr = threading.Thread(target=winTouch.exec_fork)
    winTouchThr.start()


def fork_function():
    while True:
        print '-- fork_function--'
        winTouch = WinTouch('/dev/input/event6')
        winTouch.register_listener(None)
        winTouch.exec_touch_event()

"""test"""
#run_touch_service(None)
