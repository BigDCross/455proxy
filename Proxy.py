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
            print("CONNECT found")
            return # Ignoring for now
            self.OpenTunnel(request)

        # This should eventually take an additional parameter telling it how to modify
        # the request
        #request = self.ModifyRequest(request)
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

    def OpenTunnel(self, request):
        host = request.GetHeadersDict()[b'Host']
        addr = self.GetWebAddrInfo(host[0:host.find(b':')])
        addr = (addr[0], int(host[host.find(b':') + 1:]))
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.connect(addr)
        print(addr)

        ok = b"HTTP/1.1 200 OK\r\n\r\n"

        self.SendTo(self.server_sock, request.GetMessage())
        self.SendTo(self.client_sock, ok)

        while True:
            client_data = self.client_sock.recv(4096*16)
            print("Client data: ", client_data)
            self.SendTo(self.server_sock, client_data)

            server_data = self.server_sock.recv(4096*16)
            print("Server data: ", server_data)
            self.SendTo(self.client_sock, server_data)

        self.CloseConnection(self.client_sock)

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
        while data.find(b'\r\n\r\n') == -1:
            data += sock.recv(1024)

        p = ParsedRequestMessage(data) # Not necessarily a request message. Change this
        h = p.GetHeadersDict()
        s = p.GetStatusLineTuple()

        # Some response messages must not have a message body. Check for this here.
        if p.NoMessageBodyAllowed():
            return p.GetStatusAndHeaders()

        # If chunked transfer encoding
        if b'Transfer-Encoding' in h and h[b'Transfer-Encoding'] != b'identity':
            self.ReceiveChunked(sock, data)
            #return p.GetStatusAndHeaders() # Change this

        # If Content-Length header is present
        if b'Content-Length' in h:
            to_recv = int(h[b'Content-Length']) - p.GetMessageBodyLength()
            while to_recv > 0:
                newdata = sock.recv(1024)
                data += newdata
                to_recv -= len(newdata)

        return data

    def ReceiveChunked(self, sock, data):
        print("chunked transfer encoding detected")
        print("chunked message: ", data)
        # Procedure: see (http://www.w3.org/Protocols/rfc2616/rfc2616-sec19.html#sec19.4.6)
        # Keep in mind data consists of both the headers and part (or possibly no part) of the first chunk at this point

        length = 0
        entity_body = b""

        headers = data[0:data.find(b"\r\n\r\n")]
        first_chunk = data[data.find(b"\r\n\r\n") + 4:]
        chunk_size = self.GetChunkSize(first_chunk)
        #print("chunk_size: ", chunk_size)
        first_chunk_data = first_chunk[first_chunk.find(b'\r\n') + 4:]
        #print("first_chunk_data: ", first_chunk_data)

        # Finish reading first chunk
        msg = self.RecvLen(sock, chunk_size - len(first_chunk_data))
        entity_body = first_chunk_data + msg

        length += len(entity_body)

        print("entity_body: ", entity_body, sep="\n")
        print("length of entity body: ", length, sep="\n")

        # Start of procedure from link above
        rcvd = self.RecvUntil(sock, b'\r\n')
        chunk_size = self.GetChunkSize(rcvd)

        # This grabs all the chunks until the last chunk (which has size 0) comes along
        while chunk_size > 0:
            print("Receiving: ", chunk_size + 4, "bytes")

            rcvd = self.RecvLen(sock, chunk_size + 4)

            entity_body += rcvd
            length += chunk_size

            rcvd = self.RecvUntil(sock, b'\r\n')
            chunk_size = self.GetChunkSize(rcvd)

        # Grab trailer (which consists of more headers)
        trailer = self.RecvUntil(b'\r\n\r\n')
        headers += rcvd

        print("headers: ", headers)
        print("entity_body: ", entity_body)
        print("body length: ", length)

        return

    def RecvLen(self, sock, length):
        print("Receiving", length, "bytes")
        rcvd = b""
        while length > 0:
            temp = sock.recv(length)
            length -= len(rcvd)
            rcvd += temp

        return rcvd

    def RecvUntil(self, sock, pattern):
        print("Receiving until: ", pattern)
        rcvd = b""
        while rcvd.find(pattern) == -1:
            rcvd += sock.recv(1)

        return rcvd

    def GetChunkSize(self, chunk):
        print("chunk being sized: ", chunk)
        chunk_size = int(chunk[0:chunk.find(b'\r\n')], 16)
        return chunk_size

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
            addr = (addr[0], int(host[host.find(b':') + 1:]))
        else:
            addr = self.GetWebAddrInfo(host)

        print("addr: ", addr)

        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.connect(addr)

        self.SendTo(self.server_sock, request.GetMessage())
