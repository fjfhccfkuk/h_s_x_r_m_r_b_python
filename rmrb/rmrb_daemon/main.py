#!/usr/bin/env python


import os
import multiprocessing
import time
from system import version_request

print("This is main.py , progress:" + __name__)


def __doLoadModules():
    try:
        import rmrb.modules
    except Exception, e:
        print '__doLoadModules, excp:%s' % e.message
    finally:
        print("----- import modules end -----")


def __kill_progress():
    bRet = False
    try:
        tmpDir = "/tmp/.rmrb-adc.lock"

        if not os.path.isfile(tmpDir):
            bRet = True
            return bRet


        local_file = open(tmpDir, 'r')
        strPid = local_file.readline()
#        intPid

        local_file.close()
    except Exception,e:
        print(" __kill_progress, excp:" + e.message)
    return bRet


def __write_pid():
    try:
        tmpDir = "/tmp/.rmrb-adc.lock"

        pid = os.getpid()

        local_file = open(tmpDir, 'w+')
        local_file.write(str(pid))
        local_file.close()

        print("main.__write_pid:  my pid:%d" % pid)
    except Exception, e:
        print("main.__write_pid excp:" + e.message)


def __doDaemon():

    __doLoadModules()

    __write_pid()

    while True:
        try:
            print '__doDaemon... report AppInfo ....'
            url = version_request.reportAppInfo_sync()

            url = str(url)
            print '__doDaemon... report AppInfo get url:%s' % url

            if (url != ""):
                version_request.upgradeApplication(url)
                print("update application  yes")
            else:
                print("update application  no")

        except IOError:
            print("Daemon Except: io error")
        except KeyboardInterrupt:
            print("DAemon Keyboard interrupt, hehe. do nothing")
        except Exception, e:
            print("Daemon excp:" + e.message)
        finally:
            print("Daemon finally()")
        time.sleep(30)


def runInMultiProcess():
    try:
        print("runInMultiProcess().......")
        __doDaemon()
#        p = multiprocessing.Process(target=__doDaemon)
#        p.start()

    except Exception, e:
        print("runInMultiProcess, excp: " + e.message)
    finally:
        print("")

    return


runInMultiProcess()






