#!/usr/bin/python3

import argparse
import os
import select
import socket
import sys
import threading
import time

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
        data = self.receive_request()
        tosend =  b"HTTP/1.1 200 OK\r\n"
        tosend += b"Connection: close\r\n\r\n"
        #tosend += b"Hello!\r\n\r\n"
        tosend += Input_URL_Page

        print("Sending: ")
        print(str(tosend))

        print()
        print()
        self.send_to_client(tosend)
        self.close_client_connection()

    def receive_request(self):
        data = self.client_sock.recv(1024)
        print("Received: ")
        print(str(data))

        return data

    def send_to_client(self, msg):
        self.client_sock.send(msg)

    def close_client_connection(self):
        self.client_sock.shutdown(socket.SHUT_RDWR)
        self.client_sock.close()

    #def get_webpage(self, addr):
