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

        self.CloseConnection(self.client_sock)

    def ReceiveRequest(self):
        # Procedure:
        # Call recv to get initial data
        # Find content-length header (it may not exist) to determine if
        # you should continue receiving.
        # If no content-length header: see here for details: http://www.w3.org/Protocols/rfc2616/rfc2616-sec4.html#sec4.4
        data = self.RecvFrom(self.client_sock)
        request = ParsedRequestMessage(data)

        return request

    def SendTo(self, sock, msg):
        sock.send(msg)

    # Rewrite, taking into account all the ways to receive an http message
    # (http://www.w3.org/Protocols/rfc2616/rfc2616-sec4.html#sec4.4)
    def RecvFrom(self, sock):
        data = sock.recv(1024)

        #ParsedRequestMessage.

        return data

    def CloseConnection(self, sock):
        sock.shutdown(socket.SHUT_RDWR)
        sock.close()

    def GetWebAddrInfo(self, addr):
        addrinfo = socket.getaddrinfo(addr, "http", socket.AF_INET, socket.SOCK_STREAM)
        # addrinfo is a list of addrinfos (a 5 tuple). by setting the appropriate params in getaddrinfo you can (hopefully)
        # pare this down to just one
        return addrinfo[0][4]

    # Rewrite or eliminate!
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
