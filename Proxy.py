#!/usr/bin/python3

import argparse
import os
import select
import socket
import sys
import threading
import time

from HTTPMsgUtils import *

# Send this to the client initially and they will receive a page with an input box for urls
# Make sure you prepend headers first though!
Input_URL_Page = \
b""" <!DOCTYPE html>
<html>
<body>

<form action="url_entry">
URL:<br>
<input type="text" name="url">
<br><br>
<input type="submit">
</form>

</body>
</html>
"""

class ProxyServer(threading.Thread):
    def __init__(self, client_sock, client_addr):
        super(ProxyServer, self).__init__()
        self.client_sock = client_sock
        self.client_addr = client_addr

    def run(self):
        request = self.ReceiveRequest()
        #tosend =  b"HTTP/1.1 200 OK\r\n"
        #tosend += b"Connection: keep-alive\r\n\r\n"
        #tosend += b"Hello!\r\n\r\n"
        #tosend += Input_URL_Page

        print("Received from client: ")
        print(str(request.data))

        tosend = self.GetWebPage("example.com")

        print("Sending to client: ")
        print(str(tosend))

        self.SendToClient(tosend)

        #request = self.ReceiveRequest()

        #tosend =  b"HTTP/1.1 200 OK\r\n"
        #tosend += b"Connection: keep-alive\r\n\r\n"

        self.CloseClientConnection()

    def ReceiveRequest(self):
        data = self.client_sock.recv(4096)
        request = ParsedHTTPMsg(data)

        return request

    def SendToClient(self, msg):
        self.client_sock.send(msg)

    def CloseClientConnection(self):
        self.client_sock.shutdown(socket.SHUT_RDWR)
        self.client_sock.close()

    def GetWebAddrInfo(self, addr):
        #self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        addrinfo = socket.getaddrinfo(addr, "http", socket.AF_INET, socket.SOCK_STREAM)

        return addrinfo[0][4]

    def GetWebPage(self, addr):
        print("Grabbing content from: ", addr)
        addr_info = self.GetWebAddrInfo(addr)
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.connect(addr_info)

        tosend = b"GET /index.html HTTP/1.1\r\n"
        tosend += b"HOST: "
        tosend += str.encode(addr)
        tosend += b"\r\n\r\n"
        #print(tosend)
        self.server_sock.send(tosend)

        msg = self.server_sock.recv(4096)
        #print(msg)

        return msg
