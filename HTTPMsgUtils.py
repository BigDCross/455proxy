#!/usr/bin/python3

import os
import time

# General Note: HTTP is 8 ascii all the time. Python uses unicode strings, however, so you'll
# pretty much have to prepend 'b' (indicating bytecode ) to all strings e.g. b"\r\n"

# Put utility methods here. These should not change based on message type or anything else.
def ParseHeaders(headers):
    lines = headers.split(b"\r\n")

    headers_dict = {}
    for h in lines:
        l = h[0:h.find(b": ")]
        r = h[h.find(b": ") + 2:]
        headers_dict[l] = [r]

    return headers_dict

def ParseStatusLine(status):
    s = status.split(b" ")

    # If request message
    # s[0]: request-method
    # s[1]: request-uri
    # s[2]: http-version

    # If response message
    # s[0]: http-version
    # s[1]: status-code
    # s[2]: reason-phrase
    return s[0], s[1], s[2]

# Class for parsing request messages
class ParsedRequestMessage():
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

        self.status = status_and_headers[0:status_and_headers.find(b"\r\n")]
        self.headers = status_and_headers[status_and_headers.find(b"\r\n") + 2:]
        self.body = msg

        self.headers_dict = ParseHeaders(self.headers)
        self.method, self.uri, self.http_version = ParseStatusLine(self.status)

    def GetHeaders(self):
        return self.headers

    def GetHeadersDict(self):
        return self.headers_dict

    def GetStatusLine(self):
        return self.status

    def GetStatusLineTuple(self):
        return (self.method, self.uri, self.http_version)

"""
# You can pull request messages from Request.txt for testing purposes
req_msg = b'GET http://eecs.wsu.edu/ HTTP/1.1\r\nHost: eecs.wsu.edu\r\nUser-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:42.0) Gecko/20100101 Firefox/42.0\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\nAccept-Language: en-US,en;q=0.5\r\nAccept-Encoding: gzip, deflate\r\nDNT: 1\r\nConnection: keep-alive\r\n\r\n'

p = ParsedRequestMessage(req_msg)

print(p.GetStatusLineTuple())
print(p.GetHeadersDict())
print(p.GetHeadersDict()[b"Host"])
"""
