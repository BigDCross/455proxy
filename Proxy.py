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
        print(str(request.GetMessage()))

        # Just ignoring connect requests right now
        if request.GetStatusLineTuple()[0] == b"CONNECT":
            print("CONNECT found. Ignoring")
            self.CloseConnection(self.client_sock)
            return

        # This should eventually take an additional parameter telling it how to modify
        # the request
        request = self.ModifyRequest(request)
        #print(request.GetMessage())

        print("Sending to host: ")
        print(request.GetMessage())

        self.ForwardRequestToHost(request)

        data = self.ReceiveResponse()

        print("Response received:")
        print(data)

        self.SendTo(self.client_sock, data)

        self.CloseConnection(self.client_sock)

        print("\n\n")

    def ModifyRequest(self, request):
        headers = request.GetHeadersDict()
        if b'Connection' in headers:
            headers[b'Connection'] = b'close'
        if b'Proxy-Connection' in headers:
            headers.pop(b'Proxy-Connection')

        request.headers_dict = headers

        return ParsedRequestMessage(request.Build())

    def ReceiveRequest(self):
        data = self.RecvFrom(self.client_sock)
        request = ParsedRequestMessage(data)

        return request

    def ReceiveResponse(self):
        data = self.RecvFrom(self.server_sock)
        #response = ParsedResponseMessage(data)

        return data
        #return response

    def SendTo(self, sock, msg):
        sock.send(msg)

    # Receives an http message from a socket
    # Still does not take into account all the ways to receive an http message
    # See here: (http://www.w3.org/Protocols/rfc2616/rfc2616-sec4.html#sec4.4)
    def RecvFrom(self, sock):
        # Procedure:
        # Call recv to get initial data
        # See here for details: http://www.w3.org/Protocols/rfc2616/rfc2616-sec4.html#sec4.4
        data = sock.recv(1024)

        # Grab up until end of headers at least
        while not data.find(b'\r\n\r\n'):
            data += sock.recv(1024)

        p = ParsedRequestMessage(data) # Not necessarily a request message. Change this
        h = p.GetHeadersDict()
        s = p.GetStatusLineTuple()

        # Some response messages must not have a message body. Check for this here.
        if p.NoMessageBodyAllowed():
            return p.GetStatusAndHeaders()

        # If chunked transfer encoding
        if b'Transfer-Encoding' in h and h[b'Transfer-Encoding'] != b'identity':
            # ReceiveChunked()
            return p.GetStatusAndHeaders() # Change this

        # If Content-Length header is present
        if b'Content-Length' in h:
            to_recv = int(h[b'Content-Length']) - p.GetMessageBodyLength()
            while to_recv > 0:
                newdata = sock.recv(1024)
                data += newdata
                to_recv -= len(newdata)

        return data

    def CloseConnection(self, sock):
        sock.shutdown(socket.SHUT_RDWR)
        sock.close()

    def GetWebAddrInfo(self, addr):
        addrinfo = socket.getaddrinfo(addr, "http", socket.AF_INET, socket.SOCK_STREAM)
        # addrinfo is a list of addrinfos (a 5 tuple). by setting the appropriate params in getaddrinfo you can (hopefully)
        # pare this down to just one
        return addrinfo[0][4]

    def ForwardRequestToHost(self, request):
        host = request.GetHeadersDict()[b'Host']

        if b':' in host:
            addr = self.GetWebAddrInfo(host[0:host.find(b':')])
        else:
            addr = self.GetWebAddrInfo(host)

        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.connect(addr)

        self.SendTo(self.server_sock, request.GetMessage())
