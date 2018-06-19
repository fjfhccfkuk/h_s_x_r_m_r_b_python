#!/usr/bin/env python

from core import play_ctrl
from core.media_service import media_monitor
from core.win_service import win_ctrl, win_touch_client
from core.web_service import web_socket
from core.ad_service import ad_service
import time

print "*******************  main. __name__:", __name__



#if __name__ == '__main__':

def start_main():
    import os

    """set sys environment """

    import os
#    env = dict(os.environ)
#    print '1DISPLAY:%s' % env['DISPLAY']
#    env['DISPLAY']=':0'
#    print '2DISPLAY:%s' % env['DISPLAY']

    """
    run main loop
    """
    main_ctrl = play_ctrl.play_ctrl()

    time.sleep(1)
    """ run web service """
    webSer = web_socket.run_web_service()

    time.sleep(1)
    """ run win_ctrl service"""
    winCtrl = win_ctrl.run_win_ctrl(main_ctrl)

    time.sleep(1)
    """ run media service"""
    media_monitor.run_media_monitor(main_ctrl)

    time.sleep(2)
    """run win_touch service"""
    win_touch_client.run_touch_service(winCtrl)

    """ run ad service """
    adSer = ad_service.run_ad_service()

    main_ctrl.register_ad_service(adSer)
    main_ctrl.register_web_service(webSer)
    main_ctrl.register_win_service(winCtrl)
    time.sleep(3)
    main_ctrl.loop()

start_main()



