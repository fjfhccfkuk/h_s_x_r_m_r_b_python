#!/usr/bin/python

from collections import deque
import time
from ad_req_interface import AdReqInterface
import urllib2, urllib
import threading
import uuid
import os
import json


class HttpReq(object):
    def __init__(self, type, url="http://xssp.maxbit.cn/adapi/ad/getAd"):
        self.__MAX_TIMES = 2
        self.__REQ_INTERVAL = 2
        self.__last_req_ts = 0
        self.__req_times = 0
        self.__type = type
        self.__timeout = 1
        self.__url = url
        self.__req_done = False
        self._app_id = '500098'
        self._pic_slot = '100055'
        self._video_slot = ''
        self._ad_time = '10'
        self._dev_id = ''
        self._api_ver = '1.5'

    def _set_req_done(self):
        print '_set_req_done()  _req_done = True'
        self.__req_done = True

    def set_max_times(self, t):
        self.__MAX_TIMES =t

    def set_req_interval(self, i):
        self.__REQ_INTERVAL = i

    def __update_last_req_ts(self):
        self.__last_req_ts = int(time.time())

    def __update_req_times(self):
        self.__req_times += 1

    def __update_request_counter(self):
        self.__update_last_req_ts()
        self.__update_req_times()

    def set_req_timeout(self, to):
        self.__timeout = to

    def get_req_timeout(self):
        return self.__timeout

    """ whether req node need re-add to queue """
    def need_redo(self):
        if self.__req_done:
            return False
        if self.__req_times >= self.__MAX_TIMES:
            return False

        return True

    def get_type(self):
        return self.__type

    def get_url(self):
        return self.__url

    def _do_request(self):
        raise Exception("this is method should override by subclass")

    def exec_http_req(self):
        ''' compare req interval '''
        cur_ts = int(time.time())
        dts = cur_ts - self.__last_req_ts
        if dts <= self.__REQ_INTERVAL:
            return None

        ret = self._do_request()
        self.__update_request_counter()
        return ret


class AdInfo(object):
    def __init__(self):
        self.__ad_url = None
        self.__ad_width = None
        self.__ad_height = None
        self.__ad_cb_list = []
        self.__ad_type = None
        self.__ad_media_name = None
        self.__create_time = int(time.time())
        self.__VALID_INTERVAL = 60

    def set_ad_url(self, u):
        self.__ad_url = u

        if not u:
            return
        if len(u) <= 4:
            return
        index = u.rfind('/')
        if index < 0:
            return
        name = u[index + 1:len(u)]
        self.__ad_media_name = os.path.join('/tmp/daily/index/08/pb/data/',str(name))

    def set_ad_type(self, t):
        self.__ad_type = t

    def get_ad_type(self):
        return self.__ad_type

    def set_ad_cb_add(self, l):
        self.__ad_cb_list.append(l)

    def get_ad_url(self):
        return self.__ad_url

    def get_ad_cb_list(self):
        return self.__ad_cb_list

    def get_ad_media_name(self):
        return self.__ad_media_name

    def valid(self):
        """ file doesn't exist - invalid """
        if not os.path.exists(self.__ad_media_name):
            print 'ad_service, file:%s' % self.__ad_media_name, ' does not exist'
            return False

        """ difficult time > 60s - invalid """
        ct = int(time.time())
        dt = ct - self.__create_time

        if dt > self.__VALID_INTERVAL:
            return False
        return True


class AdRequest(HttpReq):
    def __init__(self, dev_id, city_id,  type='pic'):
        super(AdRequest, self).__init__(type='REQUEST')
        self.__type = type
        self.__dev_id = dev_id
        self.__city_id = city_id
        self.__params = {}
        self.__params['id'] = str(uuid.uuid4())
        self.__params['app_id'] = self._app_id
        self.__params['adslot_id'] = self._pic_slot
        self.__params['api_version'] = self._api_ver
        self.__params['ad_time'] = self._ad_time
        self.__params['device'] = self.__generate_dev_info()
        self.__params['gps'] = self.__generate_gps_info()
        self.__params['network'] = self.__generate_network_info()
        self.__params['media'] = self.__generate_media_info()

    def __generate_media_info(self):
        media={}
        media['channel'] = 'None'
        media['tags'] = 'None'
        return media

    def __generate_gps_info(self):
        gps={}
        gps['lon'] = float(0.0)
        gps['lat'] = float(0.0)
        gps['timestamp'] = long(time.time())
        gps['city_code'] = int(self.__city_id)
        return gps

    def __generate_network_info(self):
        network = {}
        network['connection_type'] = 'UNKNOWN_NETWORK'
        network['operator_type'] = 'ISP_UNKNOWN'
        network['ipv4'] = '192.168.0.1'
        return network

    def __generate_dev_info(self):
        device = {}
        device['device_id'] = self.__dev_id
        device['vendor'] = 'rmrb'
        device['model'] = '2s'
        device['screen_width'] = int(768)
        device['screen_height'] = int(1330)
        device['os_type'] = 'UNKNOWN'
        device['os_version'] = '11.04'
        return device

    def _parse_json(self, js):

        response = AdInfo()
        while True:
            try:
                retJs = json.loads(js)
        #        retJs = json.dumps(js)
                dataJs = retJs['data']
                dataList = list(dataJs)
                lSize = len(dataList)
                dataJs = dataList[0]
                mediaUrl = dataJs['ad_url']
                response.set_ad_url(mediaUrl)

                mediaType = dataJs['ad_type']
                response.set_ad_type(mediaType)
            except Exception, e:
                print ' _parse_son, excp:%s' % e.message

            try:
                cb_url = dataJs['callback_url']
                for l in cb_url:
                    response.set_ad_cb_add(l)
            except Exception, e:
                print ' _parse_json callback_url, excp:%s' % e.message

            try:
                cb_url = dataJs['third_monitor_url']
                for l in cb_url:
                    response.set_ad_cb_add(l)
            except Exception, e1:
                print ' _parse_json third_monitor_url, excp:%s' % e1.message

            break

        return response

    def _do_request(self):
        import json
        ad_info = None
        jsObj = json.dumps(self.__params)
#        print 'adrequest json:%s' % jsObj

        con = None
        res = None

#        print 'req json:%s' % jsObj

        try:
            req = urllib2.Request(self.get_url(), jsObj.decode('utf8'), {'Content-Type': 'application/json'})
            con = urllib2.urlopen(req)
            res = con.read()
        except urllib2.HTTPError, e:
            print ' req excp:', e.message

        if con and con.code == 200 and res and len(res) > 0:
            print " success to request ad, response:\n>>>>\n%s<<<<<" % res
            ad_info = self._parse_json(res)

            if ad_info:
                self._set_req_done()
        else:
            print " failed to request ad, err code:%s\n" % con.code

        return ad_info


class AdCallback(HttpReq):
    def __init__(self, url):
        super(AdCallback, self).__init__('RESPONSE', url)

    def _do_request(self):
        print 'Am AdCallback._do_request(). '
        try:
            url = self.get_url()
            con = urllib2.urlopen(url)
            if con and con.code == 200:
                self._set_req_done()
        except urllib2.HTTPError, e:
            print ' req excp:', e.message

        return None


class AdServer(AdReqInterface):
    def __init__(self):
        """ work queue, write to left, read from right"""
        self.__work_queue = deque()

        """ ad result, write to left, read from right"""
        self.__ad_pic_queue = deque()
        self.__work_queue_lock = threading.Condition()
        self.__dev_id = None
        self.__city_id = None
        self.detect_id()

    def detect_id(self):
        f_path = '/tmp/daily/index/id.ini'
        if os.path.exists(f_path):
            f = open(f_path, 'r')
            id = f.readline()
            id = id.replace('\n', '')
            self.__dev_id = id

        """"shanghai huang-pu"""
        self.__city_id = "310101"

    def __add_pic(self, n):
        self.__ad_pic_queue.appendleft(n)

    def __get_pic(self):
        if len(self.__ad_pic_queue) == 0:
            return  None
        else:
            return self.__ad_pic_queue.pop()

    def __add_req(self, n):
        if not self.__work_queue_lock.acquire(False):
            print ' AdServer =.__add_req failed to obtain mutex lock'
            return

        if isinstance(n, HttpReq):
            self.__work_queue.appendleft(n)
            self.__work_queue_lock.notify(1)
        self.__work_queue_lock.release()

    def __get_req(self):
        if len(self.__work_queue) == 0:
            return  None
        else:
            return self.__work_queue.pop()

    def obtain_picture(self):
        path = None
        while len(self.__ad_pic_queue) > 0:
            adObj = self.__ad_pic_queue.pop()
            if not adObj.valid():
                continue

            """ add ad callback to work queue """
            cb_list = adObj.get_ad_cb_list()
            for url in cb_list:
                cb = AdCallback(url)
                self.__add_req(cb)

                path = adObj.get_ad_media_name()
            break

        """ return ad picture name usually md5value of pic """
        return path

    def obtain_video(self):
        pass

    def load_picture(self):
        """ create a new adRequest obj, add to work queue"""
        n = AdRequest(self.__dev_id, self.__city_id, 'pic')
        self.__add_req(n)

    def load_video(self):
        """ create a new adRequest obj, add to work queue"""
#        n = AdRequest("http://pricloud.cn", 'video')
#        self.__add_req(n)
        pass

    def exec_loop(self):
        while True:
            try:
                self.__work_queue_lock.acquire(True)
                while len(self.__work_queue) == 0:
                    print 'queue empty, wait here'
                    self.__work_queue_lock.wait(3)
                self.__work_queue_lock.release()

                ele = self.__get_req()
                if not isinstance(ele, HttpReq):
                    continue

                m_info = ele.exec_http_req()
                if m_info and isinstance(m_info, AdInfo):
                    if 'IMAGE' in m_info.get_ad_type():
                        self.__add_pic(m_info)

                if ele.need_redo():
                    self.__add_req(ele)
            except Exception, e:
                print ' AdServer.exec_loop() excp: ', e.message

            time.sleep(.05)


def run_ad_service():
    ad_server = AdServer()
    threading.Thread(target=ad_server.exec_loop).start()
    return ad_server


""" test """

def test():
    ad_server = run_ad_service()

    while True:
        print 'call  load_picture()'
        ad_server.load_picture()

        time.sleep(5)
        print 'call  obtain_picture()'
        name = ad_server.obtain_picture()
        print 'obtain picture name:%s' % name

        time.sleep(30)

#test()