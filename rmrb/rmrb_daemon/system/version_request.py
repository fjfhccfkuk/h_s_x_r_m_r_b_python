#!/usr/bin/env python

import sys;
import os;
from modules import sys_info
import UrlParse;
import hashlib;

this_dir, this_filename = os.path.split(__file__);
package_path = this_dir;

python_ver=sys.version_info;
major_ver = python_ver[0];
VER_ACTION_UPGRADE=1;
VER_ACTION_DONOTHING=2;

#print("major ver:" + str(major_ver));

if (major_ver == 3):
    import http.client;
if (major_ver == 2):
    import httplib;

try:
    from modules import sub_task;
except:
    print("version_request.py failed to import sub_task.");

if (major_ver == 2):
    def __doReportAppInfoWithUrl(url):

        retCode = 0;
        url = str(url).replace('\n', r'');
        updateUrl = "";
        print("__doReportAppInfoWithUrl, url:" + url);
        urlInfo = UrlParse._splieUrl(url);

        try:
            sysInfo = sys_info.init_gather_sysinfo();
            connection = httplib.HTTPConnection(
                urlInfo.getHost(),
                urlInfo.getPort(),
                timeout=3);
            reqline = urlInfo.getCmd() + "?" \
                      "Type=RMRB_APP_UPDATE" \
                      "&App=rmrb" + \
                      "&Mac=" + sysInfo.getMac() + \
                      "&Ip=" + sysInfo.getIP() + \
                      "&AppVer=" + sysInfo.getAppVer() + \
                      "&MediaVer=" + sysInfo.getMediaVer() + \
                      "&DevId=" + sysInfo.getID();

            reqline = str(reqline).replace('\n', r'');
            print("__doReportAppInfoWithUrl, request cmdline:" + reqline);

            connection.request("GET", reqline);
            response = connection.getresponse();
            retCode = response.status;
            retMsg = response.read(512);
            connection.close();

            print("__doReportAppInfoWithUrl, response:%s" % retMsg);

            if (retCode == 200 and "EMPTY" != retMsg):
                updateUrl = retMsg;

        except Exception, e:
            print("__doReportAppInfoWithUrl, excp:" + e.message + "  server ask:" + retMsg);
            updateUrl = "";

        print("__doReportAppInfoWithUrl, server ask:[%s" % retMsg + "]");
        return retCode, updateUrl;

if (major_ver == 2):
    def __doReportAppInfo():
        upgradeUrl = "";

        try:
            sysInfo = sys_info.init_gather_sysinfo();
            urls = sysInfo.getReportUrls();
            url_len = len(urls);
            if (url_len <= 0):
                print "__doReportAppInfo, url_len <= 0";
                url = "http://www.pricloud.cn:20000/rmrb/appupgrade";
                retCode, upgradeUrl = __doReportAppInfoWithUrl(url);

            while (url_len > 0):
                print "__doReportAppInfo, url_len > 0, while";
                url_len = url_len - 1;
                url = urls[--url_len];
                retCode, upgradeUrl = __doReportAppInfoWithUrl(url);
                if retCode == 200:
                    break;

            print("__doReportAppInfo, retCode:%d" % retCode)
            if retCode != 200:
                print "__doReportAppInfo, upgradeUrl empty";
#                print("__doReportAppInfo, using backup url to require upgrade.");
                url = "http://www.pricloud.cn:20000/rmrb/appupgrade";
                upgradeUrl = __doReportAppInfoWithUrl(url);

        except Exception, e:
            print("__doReportAppInfo, excp:" + e.message);
        finally:
            print("__doReportAppInfo, upgrade url:" + upgradeUrl);
            return upgradeUrl;


def reportAppInfo_sync():
    try:
        from modules import sub_task;
        sub_task.fork_task();
    except Exception,e:
        print("reportAppInfo_sync, excp:" + e.message);

    return __doReportAppInfo();

def __UnCompress(localFile):
    result = False;
    try:
        import zipfile;

        destDir = (package_path + "/../modules/");
#        destDir = sys_info.package_path;
#        destDir = '/tmp/tmp/uncompress/';
        print("__UnCompress, 1");

        print("__UnCompress, " + localFile);
        if not zipfile.is_zipfile(localFile):
            return result;

        print("__UnCompress, 2");
        fz = zipfile.ZipFile(localFile, 'r');

        print("__UnCompress, 3");
        for fn in fz.namelist():
            print("__UnCompress, name:" + fn);
            fz.extract(fn, destDir);

        print("__UnCompress, 4");
        fz.close();
        result = True;
    except Exception,e:
        print("__UnCompress, excp:" + e.message);
    finally:
        try:
            fz.close();
        except Exception:
            print("");

    return result;

def __CheckFile(localFile, md5):
    valid = False;
    md5tool = hashlib.md5();

    print("__CheckFile, localFile:" + localFile);
    try:
        if (os.path.exists(localFile) == False):
            return valid;

        f = open(localFile, 'rb');

        #Read data
        while True:
            data = f.read(4096);
            if not data:
                break;
            md5tool.update(data);

        f.close();
    except Exception,e:
        print("__CheckFile, excp:" + e.message);
    finally:
        result = md5tool.hexdigest();
        print("__CheckFile, md5 result:" + result + "    orig md5:" + md5);

        if (result == md5):
            valid = True;
        else:
            valid = False;

        return valid;

def __UpgradeModules(response, localFile, md5=""):

    try:

        print("__UpgradeModules, cur package home:" + package_path);
        print("__UpgradeModules, localfile:" + localFile + " md5:" + md5);

        f=open(localFile, 'wb');

        #read data from server
        while True:
            bin = response.read();
            if (bin == ""):
                print("__UpgradeModules, read end.");
                break;

            f.write(bin);

        f.flush();
        f.close();

        if __CheckFile(localFile, md5):
            print("__UpgradeModules, downloaded file Valid");

            """
            if not __UnCompress(localFile):
                return;
            """

            cmd  =  'dpkg -i %s' % localFile
            print '__UpgradeModules, install app command:%s' % cmd

#            os.system(cmd)

            #reload module
            print("__UpgradeModules, reloadmodules");
            reload(sub_task);
            reload(sys_info);
        else:
            print("__UpgradeModules, downloaded file Invalid");

    except Exception,e:
        print("__UpgradeModules, Exception:" + e.message);
    finally:
        print("__UpgradeModules, finally()");


def __upgradeApplicationWithUrl(url):
    upgrade = False;

    print("__upgradeApplicationWithUrl, url:" + url);

    urlInfo = UrlParse._splieUrl(url);

    try:
        while True:
            connection = httplib.HTTPConnection(
                urlInfo.getHost(),
                urlInfo.getPort(),
                timeout=3);

            reqline = urlInfo.getCmd();

#            print("__upgradeApplicationWithUrl:\n" + "schema:" + urlInfo.getSchema() + "\n" +
#                  "host:" + urlInfo.getHost() + "\n" +
#                  "port:" + urlInfo.getPort() + "\n" +
#                  "cmdLine:" + reqline + "\n"
#                  );

            connection.request("GET", reqline);
            response = connection.getresponse();
            retCode = response.status;

            #generate md5 value
            index = url.rindex('/');
            filename = url[index + 1:len(url)];
#            print("__upgradeApplicationWithUrl, filename:" + filename);
            filename = str(filename);
            index = filename.index('.');
            md5value = filename[0:index];
#            print("__upgradeApplicationWithUrl, md5value:" + md5value);

            if (retCode == 200):
                __UpgradeModules(response, "/tmp/" + md5value + ".deb", md5value);

            connection.close();

            break;
    except Exception, e:
        print("__doReportAppInfoWithUrl, excp:" + e.message);
    finally:
        return upgrade;


def upgradeApplication(url):
    try:
#        sysInfo = sys_info.init_gather_sysinfo();
#        urls = sysInfo.getUpgradeUrls();
#        urlLen = len(urls);

#        if (urlLen <= 0):
#        url="http://stream.pricloud.cn:8020/dev/bg/1.jpg";
        __upgradeApplicationWithUrl(url);

#        while (urlLen > 0):
#            print("");


    except Exception,e:
        print("upgradeApplication excp:" + e.message);
    finally:
        print("");
    return;
