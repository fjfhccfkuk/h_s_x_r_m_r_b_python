#!/usr/bin/env python


import os
import pyinotify
from threading import Thread
import media_listener
import time
"""
process media file
"""


class Media(object):
    def __init__(self, path, play_type, dura=10):
        self.__absPath=path
        self.__play_type=play_type
        self.__media_type = None
        self.__duration = dura
        pass

    def get_path(self):
        return self.__absPath

    def get_type(self):
        return self.__play_type

    def get_duration(self):
        return self.__duration

    def is_file_exist(self):
        return os.path.isfile(self.__absPath)


class MustMedia(Media):
    def __init__(self, absPath, d):
        super(MustMedia, self).__init__(path=absPath, play_type='MUST', dura=d)
        pass


class DefMedia(Media):
    def __init__(self, absPath, d):
        super(DefMedia, self).__init__(path=absPath, play_type='DEF', dura=d)
        pass


class AdvMedia(Media):
    def __init__(self, absPath, d):
        super(AdvMedia, self).__init__(path=absPath, play_type='AD', dura=d)
        pass

"""
define file detector
"""

'''file system monitor'''


class EventHandler(pyinotify.ProcessEvent):
    __who = None
    __callback=None

    def set_callback(self, cb):
        print "EventHandler set_callback()"
        self.__callback = cb

    def process_IN_ACCESS(self, event):
        print "ACCESS event:", event.pathname

    def process_IN_ATTRIB(self, event):
        print "ATTRIB event:", event.pathname

    def process_IN_CLOSE_NOWRITE(self, event):
        print "CLOSE_NOWRITE event:", event.pathname

    def process_IN_CLOSE_WRITE(self, event):
        if self.__callback:
            print "callback invoked"
            self.__callback.media_changed()
        print "CLOSE_WRITE event:", event.pathname

    def process_IN_CREATE(self, event):
        if self.__callback:
            print "callback invoked"
            self.__callback.media_changed()
        print "CREATE event:", event.pathname

    def process_IN_DELETE(self, event):
        if self.__callback:
            print "callback invoked"
            self.__callback.media_changed()
        print "DELETE event:", event.pathname

    def process_IN_MODIFY(self, event):
        print "MODIFY event:", event.pathname

    def process_IN_OPEN(self, event):
        print "OPEN event:", event.pathname

    def process_IN_MOVED_TO(self, event):
        if self.__callback:
            print "callback invoked"
            self.__callback.media_changed()
        print "MOVED_TO event:", event.pathname

    def process_IN_MOVED_FROM(self, event):
        if self.__callback:
            print "callback invoked"
            self.__callback.media_changed()
        print "MOVED_FROM event:", event.pathname

class FSMonitor(object):
    def __init__(self, des, listener, rec):
        self.__rec = rec
        self.__des = des
        self.__evnt = None
        self.__ev_handler = listener
        self.__watcher = None
        self.__callback = None
        self.__wm = pyinotify.WatchManager()
        self._timer_thr=None

    def set_event(self, ev):
        self.__evnt = ev

    def media_changed(self):
        raise Exception("this method should be override by sub class")

    def get_des(self):
        return self.__des

    def _register_callback(self, cb):
        print " FSMonitor, register_callback()"
        self.__callback = cb

    def exec_loop(self):
        if isinstance(self.__callback, media_listener.media_listener) and self.__ev_handler:
            self.__ev_handler.set_callback(self.__callback)

        while not os.path.isdir(self.get_des()):
            print " media_monitor, des:",self.get_des(), " doesn't exist, sleep 3s try again."
            time.sleep(3);

        self.media_changed()

        self.__wm.add_watch(os.path.join(self.__des, 'data'), self.__evnt, self.__rec)
        self.__watcher = pyinotify.Notifier(self.__wm, self.__ev_handler)
        self.__watcher.loop()


class MediaMonitor(FSMonitor, media_listener.media_listener):

    def __init__(self, des, listener, rec=False):
        super(MediaMonitor, self).__init__(des, listener, rec)
        self.__media_generator = None

    def register_media_generator(self, generator):
        self.__media_generator = generator

    def register_callback(self, cb):
        print " MediaMonitor, register_callback()"
        self.__callback = cb
        self._register_callback(self)

    def media_changed(self):
        print " MediaMonitor.media_changed "
        if self.__callback:
            self.__callback.media_changed()

        if self.__media_generator:
            self.__media_generator.toggle_do(self.__callback, 3)
        print " media_monitor.media_changed done"

    """
        listener is object of class media_listener
    """


class MediaListGenerator(object):

    def __init__(self, path):
        import threading
        self.__cond = threading.Condition()
        self.__wakeup = False
        self.__task_interrept = False
        self.__cb_obj = None
        self.__cb_delay = None
        self.__des_dir = path
        self.__thr = Thread(target=self.__exec_loop)
        self.__thr.start()

    def toggle_do(self, cb_obj, delay):
        self.__cond.acquire(True)
        self.__cb_delay = delay
        self.__cb_obj = cb_obj
        self.__wakeup = True
        self.__task_interrept = True
        self.__cond.notify(1)
        self.__cond.release()

    def __split_name_surfix(self, f):
        while True:
            dotIndex = f.rfind('.')
            if dotIndex <= 0:
                print 'file:[%s]' % f + " dotIndex <= 0:[%d]" % dotIndex + " [discard]"
                break
            name = f[0:dotIndex]

            surfix = f[dotIndex:len(f)]
            surfix = surfix.lower()
            if surfix != '.jpg' and surfix != '.swf' and surfix != '.gif':
                print 'file:[%s]' % f + ' surfix unknow:[%s]' % surfix + " [discard]"
                break

            if f == 'bg.jpg':
                print 'file:[%s]' % f + ' name:[%s]' % name + ' surfix:[%s]' % surfix + " dotIndex:[%d]" % dotIndex + " [discard]"
                break
            return name, surfix
        return None, None

    def __make_media_object(self, abs_path, name, duration):
        while True:
            """
            filter play type
            len(md5) == 32 + '.' = 1
            """
            if len(name) == 32:
                """play type AD"""
                media = AdvMedia(abs_path, duration)
                break
            if name.isdigit():
                """play type MUST"""
                media = MustMedia(abs_path, duration)
                break
            if name.isalpha():
                """play tpe DEF"""
                media = DefMedia(abs_path, duration)
                break
            media = None
            break
        return media

    def __split_time(self, t):

        time = None
        while True:
            if not t:
                break

            l = len(t)
            m = t.rfind('=')
            if m <= 0:
                break

            m += 1
            if m >= l:
                break

            s = t[m:l]
            if s.isdigit():
                time = s

            break

        return time

    def __generate_win_time(self, path):
        """ read show_time, hide_time, interval_time"""
        time_file = path

        t_show = 300
        t_hide = 180
        t_interval = 10

        """
        srcTime=120&IntervalTime=10&unlockTime=360
        """

        while True:
            if not os.path.exists(time_file):
                break

            with open(time_file) as tf:
                line = tf.read(512)
                line = line.replace('\n', '')
                show, interval, hide = line.split('&')
                t = self.__split_time(show)
                if t:
                    t_hide = t

                t = self.__split_time(interval)
                if t:
                    t_interval = t

                t = self.__split_time(hide)
                if t:
                    t_show = t
            break

        return int(t_show), int(t_hide), int(t_interval)

    """
        iterate destination dir, gather all file info
    """
    def __generate_media_list(self, des_dir, t_interval):
        if not os.path.exists(des_dir):
            print " des dir:%s doesn't exist" % des_dir
            return None

        media_list=[]
        files = os.listdir(des_dir)

        global media
        for f in files:
            while True:
                name, surfix = self.__split_name_surfix(f)

                if not name or not surfix:
                    print '------- invalid name or surfix'
                    break

                abs_path = os.path.join(des_dir, f)
                media = self.__make_media_object(abs_path, name, t_interval)
                if media:
                    media_list.append(media)
                break
            continue
        return media_list

    def __exec_loop(self):
        while True:

            """
                thread wait here, for new task
            """
            self.__cond.acquire(True)
            while not self.__wakeup:
                delay = 600
                if self.__cb_delay and isinstance(self.__cb_delay, int):
                    delay = self.__cb_delay
                print " MediaListGenerator running, delaying %ss" % delay
                self.__cond.wait(delay)

                if self.__task_interrept and not self.__wakeup:
                    break
                self.__wakeup = False

            print " MediaListGenerator running, ready to generate media list."
            self.__task_interrept = False
            self.__wakeup = False
            self.__cb_delay = None

            if self.__cb_obj:
                time_path = os.path.join(self.__des_dir, 'time.txt')
                t_show, t_hide, t_interval = self.__generate_win_time(time_path)
                print 'MediaListGenerator running, t_show:%d' % t_show + ' t_hide:%d' % t_hide + '  interval:%d' % t_interval
                self.__cb_obj.win_time_changed(t_show, t_hide)

                data_path = os.path.join(self.__des_dir, 'data')
                media_list = self.__generate_media_list(data_path, t_interval)
                self.__cb_obj.media_updated(media_list)
            self.__cond.release()


def run_media_monitor(main_ctrl):
    """
    create media monitor
    """

    '''define dest file/dir'''
    des = '/tmp/daily/index/08/pb/'

    '''define event to watch'''
    events = pyinotify.IN_CLOSE_WRITE | pyinotify.IN_DELETE | pyinotify.IN_MOVED_TO | pyinotify.IN_MOVED_FROM

    '''new event handler'''
    ev_handler = EventHandler()

    '''new MediaMonitor'''
    mediaSer = MediaMonitor(des=des, listener=ev_handler, rec=False)
    mediaGenerator = MediaListGenerator(mediaSer.get_des())
    mediaSer.set_event(events)
    mediaSer.register_callback(main_ctrl)
    mediaSer.register_media_generator(mediaGenerator)
    media_monitor_thr = Thread(target=mediaSer.exec_loop)
    media_monitor_thr.start()
    return mediaSer

"""
class media_listener(object):
    def media_updated(self, m_list):
        raise  Exception("this func should override by subclass")

    def media_changed(self):
        raise Excepti
        
"""


class TestClzz (media_listener.media_listener):
    def __init__(self):
        pass

    def media_updated(self, list):
        if len(list) == 0:
            print 'TestClzz.media_updated() list is none'
            return
        for m in list:
            print 'TestClzz.media_updated() abspath:[%s]' % m.get_path() + '  type:[%s]' % m.get_type()
        pass

    def media_changed(self):
        print 'TestClzz.media_changed()'

    def win_time_changed(self, t_show, t_hide):
        print 'TestClzz.win_time_changed() t_show:', t_show, '  t_hide:', t_hide


def TestFun ():
    obj = TestClzz()
    run_media_monitor(obj)

#TestFun()

