#!/usr/bin/python

from win_touch_client import TouchListener
from interface import InterfaceWinCtrl
import wnck, gtk
import webbrowser
import threading
from threading import Thread
import time


class _WinTimer(object):
    def __init__(self):
        self.__lock = threading.Condition()
        self.__reset = False
        self.__cb_obj = None
        self.__delay1 = 18000  #unit seconds
        self.__delay2 = 18000  # unit seconds
        self.__boot_flag_fake_timer2 = False
        self.__boot_time_fake_timer2 = 3

    def set_listener(self, listener):
        self.__cb_obj = listener

    def reset_timer(self, ts1, ts2, flag=False):
        print ("reset_timer 1")
        try:
            self.__lock.acquire(True)

            if self.__delay1 == 18000 or self.__delay2 == 18000:
                self.__boot_flag_fake_timer2 = True
            else:
                self.__boot_flag_fake_timer2 = flag

            self.__delay1 = ts1
            self.__delay2 = ts2

            self.__reset = True
            self.__lock.notify(1)
            self.__lock.release()
        except Exception, e:
            print " reset_timer excp:", e.message
        print 'reset_timer 5'
        print '_WinTimer reset_time, t_show:%d' % self.__delay1 + ' t_hide:%d' % self.__delay2

    def exec_timer(self):
        try:
            while True:
                self.__reset = False

                while not self.__reset:
                    self.__lock.acquire(True)
                    self.__reset = False

                    """do ring2"""
                    print "-------------- exec_timer() winTimer timer2 ring"
                    if self.__cb_obj:
                        self.__cb_obj.timer2_ring()

                    if self.__boot_flag_fake_timer2:
                        print "-------------- exec_timer() win_ctrl timer delay2 %d s" % self.__boot_time_fake_timer2
                        self.__lock.wait(int(self.__boot_time_fake_timer2))
                        self.__boot_flag_fake_timer2 = False
                    else:
                        print "-------------- exec_timer() win_ctrl timer delay2 %d s" % self.__delay2
                        self.__lock.wait(self.__delay2)

                    if self.__reset:
                        self.__reset = False
                        break;

                    """do ring1"""
                    print "-------------- exec_timer() winTimer timer1 ring"
                    if self.__cb_obj:
                        self.__cb_obj.timer1_ring()

                    print "-------------- exec_timer() win_ctrl timer delay1 %d s" % self.__delay1
                    self.__lock.wait(self.__delay1)

                    if self.__reset:
                        self.__reset = False
                        break

                    self.__reset = False
                    self.__lock.release()

                if not self.__lock.acquire(False):
                    print "-------------- exec_timer() __lock is locking"
                else:
                    print "-------------- exec_timer() __lock is unlocking"

                self.__lock.release()

        except Exception, e:
            print "exec_timer excp:", e.message


class _TimerListener(object):
    def timer1_ring(self):
        raise Exception("this method should be override by sub-class")

    def timer2_ring(self):
        raise Exception("this method should be override by sub-class")


class WinCtrl(TouchListener, InterfaceWinCtrl, _TimerListener):
    def __init__(self):
        self.__RMRB_TITLE = 'peopledaily'
        self.__RMRB_PLAYER = 'xx_zz_yy_rmrb_ss_player'
        self.__register_browser()
        self.__wins = {self.__RMRB_PLAYER: None, self.__RMRB_TITLE: None}
        self.__wins_lock = threading.Lock()
        self.__init_screen()
        self.__cb_obj = None
        self.__auto_start_win = False
        self.__timer = None
        self.__win_switch_lock = threading.Lock()
        self.__win_switcher = None
        self.__win_replace = None
        self.__time_show = 300
        self.__time_hide = 180
        self.__last_time_start_browser = 0
        self.__win_need_close = True
        self.__win_time_close = 0
        self.__win_replace_last_checking_time = 0

    def __register_browser(self):
        webbrowser.register("google-chrome", None, webbrowser.BackgroundBrowser('/usr/bin/google-chrome'))

    def __init_screen(self):
        try:
            print '\nwin_ctrl get screen default'
            self.__screen = wnck.screen_get_default()

            print '\nwin_ctrl, force_update'
            self.__screen.force_update()

            print '\nwin_ctrl, register listening for window opened closed '
            self.__screen.connect("window_opened", self.__on_win_open)
            self.__screen.connect("window_closed", self.__on_win_close)
        except Exception, e:
            print "\nWinCtrl, __init_screen excp:%s" % e.message

    def exec_loop(self):
        while True:
            while gtk.events_pending():
                gtk.main_iteration()

            if self.__win_switcher and self.__win_switch_lock.acquire(False):
                print ' gtk.events loop, do timer'
                self.__win_switcher()
                self.__win_switcher = None
                self.__win_switch_lock.release()

            if self.__win_replace:
                ct = int(time.time())
                dt = ct - self.__win_replace_last_checking_time

                if dt < 1:
                    continue

                self.__win_replace_last_checking_time = ct

                print 'win_ctrl  event_loop; win_replace [True]'
                if self.__wins_lock.acquire(False):
                    print 'win_ctrl  event_loop; obtain lock'
                    self.__wins_lock.release()
                    continue

                print 'win_ctrl  event_loop; failed to obtain lock [expect]'
                w = self.__get_win(self.__RMRB_PLAYER)
                if not w:
                    print 'win_ctrl  event_loop; no win title found'
                    continue

                print 'win_ctrl  event_loop; ready to replace win  and release win_lock'
                self.__win_replace(w)
                self.__win_replace = None
                self.__wins_lock.release()

            if self.__win_need_close:
                ct = int(time.time())
                dt = ct - self.__win_time_close
                if ct != dt and ct > self.__win_time_close:
                    w = self.__browser_exist()
                    if w:
                        print '-------------------------------------------------------------------------- do chrome close -------------------------------------------------------------------'
                        print '-------------------------------------------------------------------------- do chrome close -------------------------------------------------------------------'
                        print '-------------------------------------------------------------------------- do chrome close -------------------------------------------------------------------'
                        print '-------------------------------------------------------------------------- do chrome close -------------------------------------------------------------------'
                        print '-------------------------------------------------------------------------- do chrome close -------------------------------------------------------------------'
                        print '-------------------------------------------------------------------------- do chrome close -------------------------------------------------------------------'
                        print '-------------------------------------------------------------------------- do chrome close -------------------------------------------------------------------'
                        print '-------------------------------------------------------------------------- do chrome close -------------------------------------------------------------------'

                        w.close(0)
                        self.__wins[self.__RMRB_PLAYER] = None
                        self.__win_need_close = False
                        self.__win_time_close = 0
#            print '-------------------------- win event loop ------------------------------'
            time.sleep(.1)
        print 'win_ctrl  event_loop exit ??????'

    def register_callback(self, main_ctrl):
        self.__cb_obj = main_ctrl

    def register_timer(self, timer):
        self.__timer = timer
        self.__timer.set_listener(self)

    def reset_win_loop_time(self, t_show, t_hide):
        self.__time_hide = t_hide
        self.__time_show = t_show

        if self.__timer:
            self.__timer.reset_timer(self.__time_show, self.__time_hide, True)

    def __activate_win(self, title):
        try:
            print '__activate_win 1'
            rmrb_win = self.__get_win(title)
            print '__activate_win 2'
            if rmrb_win:
                print '__activate_win 3'
                if not rmrb_win.is_active():
                    rmrb_win.activate(0)

        except Exception, e:
            print '__activate_win, excp:', e.message

    def __timer1_ring(self):
        print " timer1 ring  ..."
        self.__activate_win(self.__RMRB_PLAYER)

    """override win_ctrl.__TimerListener"""
    def timer1_ring(self):
        if not self.__win_switch_lock.acquire(False):
            print " timer1 ring  ...failed to obtain win lock"
            return

        if self.__cb_obj:
            self.__cb_obj.on_screen_show()
        self.__win_switcher = self.__timer1_ring
        self.__win_switch_lock.release()

    def __timer2_ring(self):
        print " timer2 ring  ..."
        self.__activate_win(self.__RMRB_TITLE)

    def timer2_ring(self):
        if not self.__win_switch_lock.acquire(False):
            print " timer2 ring  ...failed to obtain win lock"
            return

        if self.__cb_obj:
            self.__cb_obj.on_screen_hide()
        self.__win_switcher = self.__timer2_ring
        self.__win_switch_lock.release()

    def __on_screen_touched(self):
        print " screen on touched ..."
        self.__activate_win(self.__RMRB_TITLE)
        self.__timer.reset_timer(self.__time_show, self.__time_hide)

    """override win_touch.TouchListener"""
    def on_screen_touched(self):
        if not self.__win_switch_lock.acquire(False):
            print " on_screen_touched  ...failed to obtain win lock"
            return
        self.__win_switcher = self.__on_screen_touched
        self.__win_switch_lock.release()

    """override InterfaceWinCtrl"""
    def start_browser(self):
        self.__auto_start_win = True
        self.__start_browser()

    """override InterfaceWinCtrl"""
    def restart_browser(self):
        pass

    def __start_browser(self):
        if not self.__auto_start_win:
            return

        cur_time = int(time.time())
        saved_time = int(self.__last_time_start_browser)
        if (cur_time - saved_time) < 10:
            print "win_ctrl.__start_browser interval time < 10s"
            return

        if not self.__wins_lock.acquire(False):
            print " win_ctrl, start_browser() failed to obtain lock"
            return

        """check does rmrb_player exist"""
        win = self.__browser_exist()
        if win:
            print " win_ctrl, start_browser() browser exist"
            """check does win is full-screen"""
            self.__wins_lock.release()
            return

        print " win_ctrl, start_browser() browser doesn't exist"
        self.__last_time_start_browser = cur_time
        self.__run_browser()
        self.__win_replace = self.__replace_rmrb_win

    def __run_browser(self):
        browser = webbrowser.get("google-chrome")
        url = "file:///home/rmrb-enewspaper/workspace/rmrb_package/opt/rmrb/html/index.html"
        browser.open_new(url)

    def __replace_rmrb_win(self, win):
        print 'win_ctrl.__replace_rmrb_win()'

        w = win
#        w = self.__get_win(self.__RMRB_PLAYER)
        if not w:
            print " win_ctrl ready to replace rmrb windows, no window found"
            return False
        else:
            print " win_ctrl ready to replace rmrb windows"
            if self.__timer:
                self.__timer.reset_timer(self.__time_show, self.__time_hide, True)

            w.set_window_type('normal')
            bitmark = (1 << 0) | (1 << 1) | (1 << 2) | (1 << 3)
            #        win.maximize()
            w.set_geometry('current', int(bitmark), 0, 0, 90, 160)
#            time.sleep(2)
            w.set_fullscreen(True)
            self.__wins[self.__RMRB_PLAYER] = w
            self.__win_time_close = int(time.time()) + 10
            return True

    def __init_win_geometry(self, win):
        if not win:
            return

#        win.activate(1)
        win.set_window_type('normal')
        bitmark = (1 << 0) | (1 << 1) | (1 << 2) | (1 << 3)
#        win.maximize()
        win.set_geometry('current', int(bitmark), 0, 0, 90, 160)
        time.sleep(2)
        win.set_fullscreen(True)

    def __on_win_open(self, screen, win):
        return

    def __on_win_close(self, screen, win):
        title = win.get_name()
        winId = win.get_xid()

        saved_win = self.__wins[self.__RMRB_PLAYER]
        if not saved_win:
            print "WinCtrl, [----- test info -----] new win closed, wid:0x%x" % winId + "  title:%s" % title  + " saved win id:None"
        else:
            print "WinCtrl, [----- test info -----] new win closed, wid:0x%x" % winId + "  title:%s" % title + " saved win id:0x%x" % saved_win.get_xid()

        if self.__RMRB_PLAYER in title:
            if self.__cb_obj:
                self.__cb_obj.on_screen_hide()

            self.__last_time_start_browser = 0
            self.__wins[self.__RMRB_PLAYER] = None
            self.__start_browser()

    def __browser_exist(self):
        return self.__wins[self.__RMRB_PLAYER]

    def __get_win(self, title):
        try:
            self.__screen.force_update()
            wins = self.__screen.get_windows()
            for w in wins:
                print '__get_win 3  title:%s' % title + "  id:0x%x" % w.get_xid() + "   win name:%s" % w.get_name()
                if title in w.get_name():
                    return w
            return None
        except Exception, e:
            print '__get_win, excp:', e.message

    def __gather_all_win_list(self):
        try:

            wins = self.__screen.get_windows()

            winDict = {}
            print "------------------------- win info ---------------------------"
            for win in wins:
                print "win id 0x%x" % win.get_xid() + " name:%s" % win.get_name()
                winDict[win.get_xid]=win.get_name()
            print "------------------------- win info ---------------------------"
            return winDict

        except Exception, e:
            print "rmrb_win_ctrl __gather_all_win_list excp:", e.message


class WinListener(object):
    def on_screen_show(self):
        raise Exception("InterfaceWinctrl should be override by subclass")

    def on_screen_hide(self):
        raise Exception("InterfaceWinctrl should be override by subclass")


def run_win_ctrl(main_ctrl):
    import threading
    import gobject

    gobject.threads_init()
    threading.Event().set()

    timer = _WinTimer()
    timerThr = Thread(target=timer.exec_timer)
    timerThr.start()

    winCtrl = WinCtrl()
    winCtrl.register_timer(timer)
    winCtrl.register_callback(main_ctrl)

    winCtrlThr = Thread(target=winCtrl.exec_loop)
    winCtrlThr.start()

    return winCtrl

"""inner test"""
def test(main_ctrl):
    import threading
    import gobject

    gobject.threads_init()
    threading.Event().set()

    timer = _WinTimer()
    timerThr = Thread(target=timer.exec_timer)
    timerThr.start()

    winCtrl = WinCtrl()
    winCtrl.register_timer(timer)
    winCtrl.register_callback(main_ctrl)

    winCtrlThr = Thread(target=winCtrl.exec_loop)
    winCtrlThr.start()

    while True:
        time.sleep(5)
        winCtrl.start_browser()

#test(None)
