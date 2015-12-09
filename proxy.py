#!/usr/bin/python3

import argparse
import os
import select
import socket
import sys
import threading
import time

HOST = ""
PORT = 5006

class BasicServer(threading.Thread):
    def __init__(self, conn):
        super(BasicServer, self).__init__()
        self.conn = conn

    def run(self):
        data = self.conn.recv(1024)
        print(data)
        tosend = "HTTP/1.1 200 OK\n"
        tosend += "Host: 127.0.0.1:5006\n"
        tosend += "Connection: close\r\n"
        tosend += "\r\n"
        tosend += "<html><body>"
        tosend += "Hello!"
        tosend += "</body></html>\r\n"
        print(tosend)
        self.conn.send(tosend)
        self.conn.close()

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))

    threads = []

    while True:
        try:
            s.listen(1)
            conn, addr = s.accept()
            print("Connected to: ", addr)

            b = BasicServer(conn)
            b.daemon = True
            b.start()

            threads.append(b)
        except KeyboardInterrupt:
            break

    print(threads)
    print(len(threads))
    for t in threads:
        t.join()

    s.shutdown(socket.SHUT_RDWR)
    s.close()

main()
