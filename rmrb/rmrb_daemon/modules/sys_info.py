#/usr/bin/env python

import os;
import time;

this_dir, this_filename = os.path.split(__file__);
package_path = this_dir;

sys_id_file = "/tmp/daily/id.ini";
media_ver_file="/tmp/daily/index/update.ini";
app_ver_file=os.path.join(package_path,"config");

class SysInfo:
    def __init__(self):
        return;

    __dev_id="-1";
    __dev_ip="-1";
    __dev_mac = "-1";
    __dev_mediaVer ="-1"
    __dev_appVer = "-1";
    __dev_issue="-1";
    __dev_report_urls=[];
    __dev_upgrade_urls = [];

    def getID(self):
        return self.__dev_id;

    def getIP(self):
        return self.__dev_ip;

    def getMac(self):
        return self.__dev_mac;

    def getSysIssue(self):
        return self.__dev_issue;

    def getMediaVer(self):
        return self.__dev_mediaVer;

    def getAppVer(self):
        return self.__dev_appVer;

    def getReportUrls(self):
        return self.__dev_report_urls;


    def getUpgradeUrls(self):
        return self.__dev_upgrade_urls;

    def setUpgradeUrls(self, urls):
        self.__dev_upgrade_urls = urls;

    def setReportUrls(self, urls):
        self.__dev_report_urls = urls;

    def setAppVer(self, ver):
        self.__dev_appVer = ver;

    def setMediaVer(self, ver):
        self.__dev_mediaVer = ver;

    def setID(self, id):
        self.__dev_id = id;

    def setIP(self, ip):
        self.__dev_ip = ip;

    def setMac(self, mac):
        self.__dev_mac = mac;

    def setSysIssue(self, issue):
        self.__dev_issue = issue;


class _InfoGather:
    app_ver = "-1";
    media_ver = "-1";
    report_urls=[];
    upgrade_urls = [];

    def __init__(self):
        try:
            if (os.path.isfile(app_ver_file) == False):
                print("app_ver_file doesn't exist. file:" + app_ver_file);
                return;

            f = open(app_ver_file, 'r');

            while (True):
                try:
                    line = f.readline();

                    if (line == ""):
                        break;

                    if(line.__contains__("version")):
                        str = line.split("$");
                        _InfoGather.app_ver = str[1].replace("\n","");
                        continue;

                    if(line.__contains__("report_urls")):
                        str = line.split("$");
                        urls = str[1];
                        _InfoGather.report_urls = urls.split(",");
                        continue;

                    if (line.__contains__("upgrade_urls")):
                        str = line.split("$");
                        urls = str[1];
                        _InfoGather.upgrade_urls = urls.split(",");
                        continue;

                    continue;
                except IndexError, e:
                    print("IndexExcp:" + e.message);
                except Exception,e:
                    print("AllExcp:" + e.message);

            f.close();
        except Exception,e:
            print("#################################  Excp:" + e.message);
        finally:
            return;

    def gatherUrls(self):
        return _InfoGather.report_urls;

    def gatherDevid(self):
        id="-1";
        if (os.path.isfile(sys_id_file)):
            f = open(sys_id_file, 'r');
            id = f.read();
            id.replace("\n", "");
            f.close();

        return id;

    def gatherMediaVer(self):
        try:
            if (os.path.isfile(media_ver_file)):
                f = open(media_ver_file, 'r');
                line = f.readline();
                f.close();

                _InfoGather.media_ver = line.replace('\n', '', 1);
        except Exception, e:
            print("gatherMediaVer, excp:" + e.message);
        finally:
            return _InfoGather.media_ver;

    def gatherIP(self):
        ip="0.0.0.0";
        try:
            import socket
            s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("114.114.114.114", 80))
            ip=s.getsockname()[0]
        except:
            return ip;
        return ip;

    def gatherMac(self):
        mac="00:00:00:00:00:00";
        try:
            if not os.path.exists("/sys/class/net/eth0/address"):
                return mac;

            macFile = open("/sys/class/net/eth0/address")
            macStr = macFile.readline();
            mac = macStr.replace("\n", "");
            macFile.close()
        except Exception,e:
            print "get mac excp:" + e.message;

        return mac;

    def gatherAppVer(self):
        return _InfoGather.app_ver;

    def gatherUpgradeUrl(self):
        return _InfoGather.upgrade_urls;


def init_gather_sysinfo():
    sysInfo = SysInfo();
    infoGather = _InfoGather();

    id = infoGather.gatherDevid();
    mVer = infoGather.gatherMediaVer();
    appVer = infoGather.gatherAppVer();
    urls = infoGather.gatherUrls();
    upgradeUrls=infoGather.gatherUpgradeUrl();
    ip=infoGather.gatherIP()
    mac = infoGather.gatherMac();

    sysInfo.setID(id);
    sysInfo.setMediaVer(mVer);
    sysInfo.setAppVer(appVer);
    sysInfo.setReportUrls(urls);
    sysInfo.setUpgradeUrls(upgradeUrls);
    sysInfo.setMac(str(mac));
    sysInfo.setIP(str(ip))

    del infoGather;
    return sysInfo;