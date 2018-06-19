#!/usr/bin/env python

def __get_xorg_pid():
    pid=-1;
    try:
        import os;
        pid = os.popen('ps aux | grep "/usr/bin/X" | grep -v "grep" | awk \'{print $2}\'').read();
#        print "__get_xorg_pid. pid:" + str(pid);
    except:
        pid=-1
    return pid;


def __get_vlc_pid():
    pid = -1;
    try:
        import os;
        pid = os.popen('ps aux | grep "vlc" | grep "sh" | grep -v "grep" | awk \'{print $2}\'').read();
#        print "__get_vlc_pid. pid:" + str(pid);
    except:
        pid = -1
    return pid;


def __get_xorg_socket_count():
    count=0
    try:
        import os;

        while True:
            xorgPid = __get_xorg_pid()
#            print "xorg pid:" + xorgPid
            if xorgPid == "":
                break;

            xorgPid = xorgPid.replace("\n", "");
            cmd = "sudo lsof -p %s" % xorgPid + " | grep socket | wc -l"
            ret = os.popen(cmd).read();
            ret = ret.replace("\n", "")
            if ret == "":
                break;

            tmpInt = int(ret)
            count = tmpInt;
            break;
    except Exception,e:
        print "excp:" + e.message
        count=0;
    return count;


def __do_kill_vlc():
    try:
        import os
        xorg_count = __get_xorg_socket_count() #MAX_XORG_CONT=210
        if xorg_count >= 210:
            pid = __get_vlc_pid()
            cmd = "sudo kill -9 %s" % pid
            os.popen(cmd).read()
    except Exception, e:
        print "__do_kill_vlc excp:" + e.message
    return;


def do_monitor_vlc():
    __do_kill_vlc()


def debug_xorg_monitor():

    retStr = "sorry,nothing"

    try:
        count =  __get_xorg_socket_count()
        retStr = "xorg_socket_count:[%d" % count + "]";

        xorg_pid = __get_xorg_pid();
        retStr += "xorg_pid:[%s" % xorg_pid + "]";

        vlc_pid = __get_vlc_pid()
        retStr += " vlc_pid:[%s" % vlc_pid + "]";
    except Exception,e:
        print ""
    return retStr.replace("\n", "");

