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
        headers_dict[l] = r

        # If comma seperated turn into list
        if r.find(b',') != -1:
            headers_dict[l] = r.split(b',')

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

class HTTPMessage():
    def __init__(self, status_tuple, headers_dict, body):
        self.status_tuple = status_tuple
        self.headers_dict = headers_dict
        self.body = body

    def GetStatusAsString(self):
        return self.status_tuple[0] + b" " + self.status_tuple[1] + b" " + self.status_tuple[2] + b"\r\n"

    def GetHeadersAsString(self):
        s = b""
        for k in self.headers_dict.keys():
            if isinstance(self.headers_dict[k], list):
                s += k + b": " + b",".join(self.headers_dict[k]) + b"\r\n"
            else:
                s += k + b": " + self.headers_dict[k] + b"\r\n"

        s += b"\r\n"
        return s

    def GetMessageBody(self):
        return self.body

    def Build(self):
        return self.GetStatusAsString() + self.GetHeadersAsString() + self.GetMessageBody()

# Class for parsing request messages
class ParsedRequestMessage():
    def __init__(self, data):
        self.msg = data
        self.parse()

    def parse(self):
        s = self.msg.split(b"\r\n\r\n")
        try:
            self.status_and_headers = s[0]
        except:
            self.status_and_headers = b""
        try:
            msg = s[1]
        except:
            msg = b""

        self.status = self.status_and_headers[0:self.status_and_headers.find(b"\r\n")]
        self.headers = self.status_and_headers[self.status_and_headers.find(b"\r\n") + 2:]
        self.body = msg

        self.headers_dict = ParseHeaders(self.headers)
        self.method, self.uri, self.http_version = ParseStatusLine(self.status)

    def NoMessageBodyAllowed(self):
        return False

    def GetMessage(self):
        return self.msg

    def GetStatusAndHeaders(self):
        return self.status_and_headers

    def GetHeaders(self):
        return self.headers

    def GetHeadersDict(self):
        return self.headers_dict

    def GetStatusLine(self):
        return self.status

    def GetStatusLineTuple(self):
        return (self.method, self.uri, self.http_version)

    def GetMessageBody(self):
        return self.body

    def GetMessageBodyLength(self):
        if self.body:
            return len(self.body)
        else:
            return 0

    def GetStatusAsString(self):
        s = self.GetStatusLineTuple()
        return s[0] + b" " + s[1] + b" " + s[2] + b"\r\n"

    def GetHeadersAsString(self):
        s = b""
        for k in self.headers_dict.keys():
            if isinstance(self.headers_dict[k], list):
                s += k + b": " + b",".join(self.headers_dict[k]) + b"\r\n"
            else:
                s += k + b": " + self.headers_dict[k] + b"\r\n"

        s += b"\r\n"
        return s

    def GetMessageBody(self):
        return self.body

    def Build(self):
        return self.GetStatusAsString() + self.GetHeadersAsString() + self.GetMessageBody()

"""
# You can pull request messages from Request.txt for testing purposes
req_msg = b'GET http://eecs.wsu.edu/ HTTP/1.1\r\nHost: eecs.wsu.edu\r\nUser-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:42.0) Gecko/20100101 Firefox/42.0\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\nAccept-Language: en-US,en;q=0.5\r\nAccept-Encoding: gzip, deflate\r\nDNT: 1\r\nConnection: keep-alive\r\n\r\n'

p = ParsedRequestMessage(req_msg)

print(p.GetStatusLineTuple(), end="\n\n")
print(p.GetHeadersDict(), end="\n\n")
print(p.GetHeadersDict()[b"Host"], end="\n\n")

h = HTTPMessage(p.GetStatusLineTuple(), p.GetHeadersDict(), p.GetMessageBody())
print(h.Build(), end="\n\n")
"""
