#!/usr/bin/python3

import argparse
import os
import select
import socket
import sys
import threading
import time

from HTTPMsgUtils import *

class ProxyServer(threading.Thread):
    def __init__(self, client_sock, client_addr):
        super(ProxyServer, self).__init__()
        self.client_sock = client_sock
        self.client_addr = client_addr

    def run(self):
        # Procedure:
        # Receive http request msg from browser
        # Pull out host from request (see Hausers email for important caveat)
        # Get address info for host
        # Create a socket with requested host.
        # Send request msg (possibly changed) to host
        # Receive response message from host
            # This is the tricky part. Need to take into account content-length, chunked transfer
            # encoding, etc to make sure we receive the full message.
        # Send response message to browser
        # If chunked transfer encoding is used loop and continue receiving from host?
        # Close connection. (Threads run method will return and thread will die)

        request = self.ReceiveRequest()

        print("Received from client: ")
        print(str(request.data))

        #print(request.GetStatusLineTuple())
        #tosend = self.GetWebPage("example.com")
        #tosend = self.GetWebPage("eecs.wsu.edu/~hauser/cs455/index.html")
        #tosend = self.GetWebPage(request.GetStatusLineTuple()[1])

        #print("Sending to client: ")
        #print(str(tosend))

        #self.SendToClient(tosend)

        #request = self.ReceiveRequest()

        #tosend =  b"HTTP/1.1 200 OK\r\n"
        #tosend += b"Connection: keep-alive\r\n\r\n"

        self.CloseClientConnection()

    def ReceiveRequest(self):
        data = self.client_sock.recv(1024*16)
        request = ParsedRequestMessage(data)

        return request

    def SendToClient(self, msg):
        self.client_sock.send(msg)

    def CloseClientConnection(self):
        self.client_sock.shutdown(socket.SHUT_RDWR)
        self.client_sock.close()

    def GetWebAddrInfo(self, addr):
        #self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        addrinfo = socket.getaddrinfo(addr, "http", socket.AF_INET, socket.SOCK_STREAM)

        print(addrinfo)

        return addrinfo[0][4]

    def GetWebPage(self, addr):
        print("Grabbing content from: ", addr)
        host = None
        filename = b"/index.html"
        if addr.find(b"/") != -1:
            host = addr[:addr.find(b"/")]
            filename = addr[addr.find(b"/"):]
        else:
            host = addr

        addr_info = self.GetWebAddrInfo(host)
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.connect(addr_info)

        tosend = b"GET "
        tosend += str.encode(filename)
        tosend += b" HTTP/1.1\r\n"

        tosend += b"HOST: "
        tosend += str.encode(host)
        tosend += b"\r\n\r\n"
        print("Sending request to webaddress ", host, ":", sep="")
        print(tosend)
        self.server_sock.send(tosend)

        msg = self.server_sock.recv(1024*16)
        #print(msg)

        return msg
