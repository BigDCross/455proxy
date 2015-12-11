#!/usr/bin/python3

import os
import time

# Class for building http request messages
class RequestMsg():
    def __init__(self):
        pass

    def AddHeader(self):
        pass

    def BuildMsg(self):
        return self.msg

# Class for parsing http messages
class ParsedHTTPMsg():
    def __init__(self, data):
        self.data = data
        self.parse()

    def parse(self):
        s = self.data.split(b"\r\n\r\n")
        try:
            status_and_headers = s[0]
        except:
            status_and_headers = None
        try:
            msg = s[1]
        except:
            msg = None

        #print(status_and_headers)
        #print(msg)

        self.status = status_and_headers[0:status_and_headers.find(b"\r\n")]
        self.headers = status_and_headers[status_and_headers.find(b"\r\n") + 2:]
        self.body = msg
        #print(self.status)
        #print(self.headers)
        #print(self.body)

        self.ParseHeaders()

        #print()

    def ParseHeaders(self):
        lines = self.headers.split(b"\r\n")

        self.headers_dict = {}
        for h in lines:
            l = h[0:h.find(b": ")]
            r = h[h.find(b": ") + 2:]
            self.headers_dict[l] = [r]
        #print(self.headers_dict)

    def GetHeaders(self):
        return self.headers

    def GetHeadersDict(self):
        return self.headers_dict

"""
req_msg = b"GET /path/file.html HTTP/1.0\r\nFrom: someuser@jmarshall.com\r\nUser-Agent: HTTPTool/1.0\r\n\r\n"

reply_msg = b"HTTP/1.0 200 OK\r\nDate: Fri, 31 Dec 1999 23:59:59 GMT\r\nContent-Type: text/html\r\n\r\n"
reply_msg += b"<html>\r\n<body>\r\n<h1>Happy New Millennium!</h1>\r\n</body>\r\n</html>"

p = ParsedHTTPMsg(req_msg)
p = ParsedHTTPMsg(reply_msg)
"""
