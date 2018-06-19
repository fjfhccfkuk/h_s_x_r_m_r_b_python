#!/usr/bin/python


import time
from threading import Thread, Lock
from media_service import media_listener
from win_service.win_ctrl import WinListener
import threading


class play_ctrl(media_listener.media_listener, WinListener):
    def __init__(self):
        self.__CUR_LOOP_STATE="PAUSE"
        self.__thread_mutex = threading.Condition()
        self.__media_list = None
        self.__win_service = None
        self.__web_service = None
        self.__ad_service  = None
        self.__play_cursor = 0
        self.__play_list = []
        self.__win_showing = False
        self.__media_changing = False
        self.__WAITTING_TIME = 300
        self.__saved_win_show_time = 0
        self.__saved_win_hide_time = 0

    """
     OverrideClass media_listener.media_updated() 
    """
    def win_time_changed(self, t_show, t_hide):
        if self.__saved_win_show_time == t_show and self.__saved_win_hide_time == t_hide:
            return

        if self.__win_service:
            self.__win_service.reset_win_loop_time(t_show, t_hide)
            self.__saved_win_show_time = t_show
            self.__saved_win_hide_time = t_hide

    """
     OverrideClass media_listener.media_updated() 
    """
    def media_updated(self, m_list):
        print " play_ctrl.media_updated "
        self.__thread_mutex.acquire(True)
        self.__media_list = m_list
        self.__thread_mutex.notify(1)
        self.__thread_mutex.release()
        print " play_ctrl.media_updated done"

    def media_changed(self):
        print " play_ctrl.media_changed "
        self.__thread_mutex.acquire(True)
        self.__media_changing = True
        self.__thread_mutex.notify(1)
        self.__thread_mutex.release()
        print " play_ctrl.media_changed done"

    """Override rmrb_win_ctrl.WinListener"""
    def on_screen_show(self):
        print 'play_ctrl.on_screen_show()'
        self.__thread_mutex.acquire(True)
        self.__win_showing = True
        self.__thread_mutex.notify(1)
        self.__thread_mutex.release()

    """Override rmrb_win_ctrl.WinListener"""
    def on_screen_hide(self):
        print 'play_ctrl.on_screen_hide()'
        self.__thread_mutex.acquire(True)
        self.__win_showing = False
        self.__thread_mutex.notify(1)
        self.__play_cursor = 0
        self.__thread_mutex.release()

    def register_ad_service(self, obj):
        self.__ad_service = obj

    def register_web_service(self, obj):
        self.__web_service = obj

    def register_win_service(self, obj):
        self.__win_service = obj

    def __get_next_media(self):
        self.__play_cursor %= len(self.__play_list)
        media = self.__play_list[self.__play_cursor]
        self.__play_cursor += 1
        return media

    def __get_next_media_type(self):
        self.__play_cursor %= len(self.__play_list)
        media = self.__play_list[self.__play_cursor]
        return media.get_type()

    def loop_RUNNING(self):

        print "play_ctrl, main loop [RUNNING]"

        """ when media changing -> PAUSE """
        if self.__media_changing:
            if self.__media_list:
                print 'play_ctrl.loop_RUNNING state [ media updating ]'
                self.__update_media_list()
            else:
                print 'play_ctrl.loop_RUNNING state [ media changing ]'
                self.__CUR_LOOP_STATE = "PAUSE"
            return
        print 'play_ctrl.loop_RUNNING state [ media state OK ]'

        """ when media_using is empty -> PAUSE"""
        if not self.__play_list:
            print 'play_ctrl.loop_RUNNING state [ media list empty ]'
            self.__CUR_LOOP_STATE = "PAUSE"
            return
        print 'play_ctrl.loop_RUNNING state [ media list OK ]'

        """ when win_ctrl is empty -> PAUSE"""
        if not self.__win_service:
            print 'play_ctrl.loop_RUNNING state [ win ctrl None ]'
            self.__CUR_LOOP_STATE = "PAUSE"
            return
        print 'play_ctrl.loop_RUNNING state [ win ctrl OK ]'

        """ start browser """
        self.__win_service.start_browser()

        """ cur win hide -> PAUSE"""
        if not self.__win_showing:
            print 'play_ctrl.loop_RUNNING state [ win not showing ]'
            self.__CUR_LOOP_STATE = "PAUSE"
            return
        print 'play_ctrl.loop_RUNNING state [ win OK ]'

        if not self.__web_service:
            print 'play_ctrl.loop_RUNNING state [ web server None ]'
            self.__CUR_LOOP_STATE = "PAUSE"
            return

        next_media_type = self.__get_next_media_type()
        print 'play_ctrl.loop_RUNNING state [ web server OK ]'
        media = self.__get_next_media()

        absPath = media.get_path()
        if 'DEF' in next_media_type and self.__ad_service:
            path = self.__ad_service.obtain_picture()
            if path:
                absPath = path

        print "play_ctrl.loop_RUNNING state sending %s to client" % absPath + " type:%s" % media.get_type()
        self.__web_service.send_media(absPath)

        next_media_type = self.__get_next_media_type()
        if 'DEF' in next_media_type and self.__ad_service:
            self.__ad_service.load_picture()

        self.__thread_mutex.wait(media.get_duration())


    def loop_AD_REQUEST(self):
        print "play_ctrl, main loop [AD_REQUEST]"

    def loop_AD_RESPONSE(self):
        print "play_ctrl, main loop [AD_RESPONSE]"

    def loop_PAUSE(self):
        print "play_ctrl, main loop [PAUSE]"
        self.__thread_mutex.wait(self.__WAITTING_TIME)
        self.__CUR_LOOP_STATE = 'RUNNING'

    def __update_media_list(self):
        print "play_ctrl, main loop [MEDIA_UPDATED]"

        while True:
            if not self.__media_list:
                print "play_ctrl, main loop [MEDIA_UPDATED] media_list none"
                self.__CUR_LOOP_STATE = "PAUSE"
                break

            m_def = []
            m_ad = []
            self.__play_list = []
            self.__play_cursor = 0

            for media in self.__media_list:
                print "play_ctrl MEDIA_UPDATED----->>>>path:", media.get_path() + " type:", media.get_type() + " duration:", media.get_duration()

                m_type = media.get_type()
                if m_type == 'MUST':
                    self.__play_list.append(media)
                    continue
                if m_type == 'DEF':
                    m_def.append(media)
                    continue
            if len(m_def) != 0:
                for m in m_def:
                    self.__play_list.append(m)
                    print "play_ctrl MEDIA_UPDATED  add to play list ----->>>>path:", m.get_path() + " type:", m.get_type() + " duration:", m.get_duration()
            else:
                break
            """ every time media updating, should update pb.swf """
            if self.__web_service:
                self.__web_service.send_media("/tmp/daily/index/08/pb.swf")
            break

        self.__media_list = None
        self.__media_changing = False
        self.__CUR_LOOP_STATE = "RUNNING"
        """release tmp list"""
        print "play_ctrl MEDIA_UPDATED----->>>> media_play size: %d" % len(self.__play_list)

    __loop_state = {
        "RUNNING":          loop_RUNNING,
        "PAUSE":            loop_PAUSE,

        "AD_REQUEST":       loop_AD_REQUEST,
        "AD_RESPONSE":      loop_AD_RESPONSE,
    }

    ''' main loop '''
    def loop(self):
        while True:
            try:
                self.__thread_mutex.acquire()
                self.__loop_state[self.__CUR_LOOP_STATE](self)
                self.__thread_mutex.release()
            except Exception,e:
                print "play_ctrl, main loop excp:", e.message
                self.__thread_mutex.release()
                time.sleep(.5)


