#!/usr/bin/env python

import os;

class UrlInfo:
    __schema="";
    __host="";
    __port="";
    __cmd="";
    __method="GET";

    def getSchema(self):
        return self.__schema;

    def getHost(self):
        return self.__host;

    def getPort(self):
        return self.__port;

    def getCmd(self):
        return self.__cmd;

    def getMethod(self):
        return self.__method;

    def setSchema(self, s):
        self.__schema = s;

    def setMethod(self, s):
        self.__method = s;

    def setCmd(self, s):
        self.__cmd = s;

    def setPort(self, s):
        self.__port = s;

    def setHost(self, s):
        self.__host = s;


def _splieUrl(url):
        urlInfo = UrlInfo();

        try:
            # get Port
            urlLen = len(url);
            portIndex = url.rindex(":");
            portStr = url[portIndex + 1:urlLen];
            urlInfo.setPort(portStr);

            # get cmd
            cmdIndex = portStr.index("/", 0, urlLen - portIndex - 1);
            cmdStr = portStr[cmdIndex:urlLen];
            urlInfo.setCmd(cmdStr);
            portStr = portStr[0:cmdIndex];
            urlInfo.setPort(portStr);

#            print("_splieUrl(), cmdStr:" + cmdStr + " portStr:" + portStr + "  orig url:" + url);

            # get host
            strUrl = str(url);
            strList = strUrl.split("//");
            strLen = len(strList);

            if (strLen <=0):
                schema = "unknow";
                urlInfo.setSchema(schema);
                urlInfo.setHost("invalid");
            else:
                tmpStr = strList[0];
                schema = strList[0] + "//";
#                print("schema:-----------------:" + schema + "  strList[0]:" + strList[0]);
                urlInfo.setSchema(schema);
                startIndex = len(schema);
                endIndex = strUrl.rindex(":");
                host = strUrl[startIndex:endIndex];
                urlInfo.setHost(host);
            # get schema

        except Exception, e:
            print("_splieUrl(), Excp:" + e.message);
        finally:
            return urlInfo;


