#!/usr/bin/env python

print("SUB_TASK, Hello, Am sub_task");

import os;
import hashlib;
import time;
import multiprocessing;

def __getMd5(localFile):
    md5Value = "";
    md5tool = hashlib.md5();

    print("__CheckFile, localFile:" + localFile);
    try:
        if (os.path.exists(localFile) == False):
            return md5Value;

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
        md5Value = md5tool.hexdigest();
        return md5Value;

def __Compress(localpath, desfile):
    result = False;

    try:
        import zipfile;

        f = zipfile.ZipFile(desfile, 'w', zipfile.ZIP_DEFLATED)
        for dirpath, dirnames, filenames in os.walk(localpath):
            for filename in filenames:
                f.write(os.path.join(dirpath, filename));
        result = True;
    except Exception,e:
        print("__Compress, excp:" + e.message);
    finally:
        try:
            f.close();
        except Exception:
            print("");

    return result;

def __file_packet():
    result = False;
    desFile = "";
    pbMd5 = "";

    srcFile = "/tmp/rmrb_syslog.zip";

    if __Compress("/tmp/daily/index/08/", srcFile):
        result = True;
        print("__file_packet, compress ok :" + srcFile);
    else:
        return result;

    if not os.path.isfile(srcFile):
        return pbMd5, desFile, result;

    pbMd5 = __getMd5(srcFile);

    desFile = os.path.join('/tmp/', '%s.zip' % pbMd5);
    os.rename(srcFile, desFile);

    print("__file_packet, " + pbMd5 + "  " + desFile + "  " + str(result));
    return pbMd5, desFile, result;

def __test_transport1():
    url = "http://pricloud.cn:20000/appupgrade/"
    try:
        import httplib;
        from system import post_form;

        connection = httplib.HTTP("pricloud.cn:20000");
        connection.putrequest('POST', '/appupgrade/appupgrade');
        content_type, body = post_form.encode_multipart_formdata(['/tmp/c3052ec34a35cffac476a65a08b4dd2d.zip']);
        print "Header content_type:" + content_type
        connection.putheader('content-type', content_type)
        connection.putheader('content-length', str(len(body)))
        connection.endheaders()
        connection.send(body)
        errcode, errmsg, headers = connection.getreply()
        print errcode
        print errmsg
        print headers
#        for l in connection.getfile():
#            print l

        connection.close();

#        if not 1:
#            return connection.file.read()
#            f = open(file, 'rb')
#            sys.stdout.write(f.read())
#            mmapped_file_as_string = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
#            request = urllib2.Request(url, mmapped_file_as_string)
#            request.add_header('Content-Type', content_type)
#            response = urllib2.urlopen(request)
#            mmapped_file_as_string.close()
#            f.close()

    except Exception,e:
        print("__test_transport1, excp:" + e.message);
    finally:
        print("");


def __test_transport():
    try:

        import urllib2;
        from system import post_form;
        from cStringIO import StringIO;
        from io import StringIO;
        from io import BytesIO;

        form = post_form.multi_part_form()
        form.add_file('file', '/tmp/c3052ec34a35cffac476a65a08b4dd2d.zip', file_obj=BytesIO('/tmp/c3052ec34a35cffac476a65a08b4dd2d.zip'))

#        request = urllib2.Request('http://127.0.0.1:8080/appupgrade/appupgrade')
        request = urllib2.Request('http://pricloud.cn:20000/appupgrade/appupgrade')
        body = str(form)
        request.add_header('Content-type', 'multipart/form-data; boundary=####')
        request.add_header('Content-length', len(body))
        request.add_data(body)

        print request.headers
        print body;
        print "**************************************"
        print 'Request'
        print request.get_data()

        print 'Response'
        print urllib2.urlopen(request);
        print "**************************************"

    except Exception,e:
        print("__test_transport, excep:" + e.message);


def __file_transport2(md5Val, desFile):
    try:
        import urllib2;
        from system import post_form;
        from system.poster.encode import multipart_encode
        from system.poster.streaminghttp import register_openers
        register_openers();
        datagen, headers = multipart_encode({"LOG_%s" % md5Val: open(desFile, "rb")})
#        request = urllib2.Request('http://pricloud.cn:20000/appupgrade/appupgrade', datagen, headers)
        request = urllib2.Request('http://pricloud.cn:20000/rmrb/appupgrade', datagen, headers)
        print "__file_transport2 " + str(request.headers)
        print "__file_transport2 " + str(datagen);
        print "****************__file_transport2*******************"
        print "__file_transport2  Request"
        print request.get_data()
        print "__file_transport2, Response"
        print urllib2.urlopen(request);
        print "****************__file_transport2*******************"
    except Exception,e:
        print("__file_transport2, excep:" + e.message);


def __file_transport(md5Val, desFile):

    print("__file_transport md5Val:" + md5Val + " desFile:" + desFile);
    try:
        import zipfile;
        import urllib;
        import urllib2;

        if not os.path.isfile(desFile):
            return;

        if not zipfile.is_zipfile(desFile):
            return;

        reqStr = "http://pricloud.cn:20000/appupgrade/?type=upload&name=rmrb_pb&md5=" + md5Val;
        print("__file_transport, reqStr:" + reqStr);

        with open(desFile, 'r') as uploadFile:
            content = uploadFile.read();
        postdata={'file':content};
        request = urllib2.Request(reqStr, data=urllib.urlencode(postdata));
        response = urllib2.urlopen(request);
        retCode = response.status;

        print("__file_transport, upload retCode:" + retCode);
        uploadFile.close();

    except Exception,e:
        print("__file_transport, excp:" + e.message);
    finally:
        print("");

    return;


def __need_update(md5Val):
    need = False;

    try:
        import httplib;
        import sys_info;
        from modules import xorg_monitor as xorg
        sysInfo = sys_info.init_gather_sysinfo();
        urls = sysInfo.getReportUrls();

        connection = httplib.HTTPConnection("pricloud.cn", 20000, timeout=3);
        reqline = "/rmrb/appupgrade?Type=RMRB_SP_INFO&App=rmrb&SP=%s" % md5Val + \
            "&Mac=" + sysInfo.getMac() + \
            "&Ip=" + sysInfo.getIP() + \
            "&AppVer=" + sysInfo.getAppVer() + \
            "&MediaVer=" + sysInfo.getMediaVer() + \
            "&DevId=" + sysInfo.getID() + \
            "&Debug=" + xorg.debug_xorg_monitor();

        reqline = reqline.replace(" ",  "");
        reqline = reqline.replace("\n", "")
        print("__need_update, request cmdline:" + reqline);

        connection.request("GET", reqline);
        response = connection.getresponse();
        retCode = response.status;
        retMsg = response.read(16);
        connection.close();

        print("__need_update, retMsg:" + retMsg);

        if ((retCode == 200) and (retMsg == "TRUE")):
            need = True;

    except Exception, e:
        print("__need_update, excp:" + e.message);
    finally:
        print("__need_update, finally");

    print("__need_update, need to upload ? %s" % str(need));
    return need;


def __file_process():
    while True:
        try:
            md5Val,desFile,result = __file_packet();
            if not result:
                break;

            if not __need_update(md5Val):
                break;

            if desFile == "":
                break;

            __file_transport2(md5Val, desFile);

        except Exception,e:
            print("__file_process, excp:" + e.message);
        finally:
            break;

    print("__file_process, done");
    return;


def __reload_modules():
    try:
        flag="/opt/rmrb/reboot"

        if not os.path.isfile(flag):
            return

        """delete flag file"""
        os.remove(flag)
        os.system('sudo reboot')

    except:
        return;
    return;


def fork_task():
#    __file_process()
    __reload_modules()
    try:
        import xorg_monitor as xorg
        xorg.do_monitor_vlc()
    except:
        print "";
    return;