#!/usr/bin/python3

import argparse
import socket

from Proxy import ProxyServer

HOST = ""
PORT = 5006

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))

    threads = []

    Running = True
    while Running:
        try:
            s.listen(1)
            outsock, addr = s.accept()
            print("Connected to: ", addr)

            b = ProxyServer(outsock, addr)
            #b.daemon = True
            b.start()
            #outsock.close()

            threads.append(b)

            for t in threads:
                if not t.isAlive():
                    t.join()
                    threads.remove(t)
        except KeyboardInterrupt:
            Running = False

    for t in threads:
        if not t.isAlive():
            t.join()
            threads.remove(t)

    s.shutdown(socket.SHUT_RDWR)
    s.close()

main()
