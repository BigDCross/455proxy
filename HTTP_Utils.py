#!/usr/bin/python3

import os
import time

# Class for building http request messages
class RequestMsg():
    def __init__(self):
        pass

    def AddHeader(self):
        pass

    def BuildMsg(self):
        return self.msg

# Class for parsing http request messages
class ParseRequestMsg():
    def __init__(self, msg):
        self.msg = msg
        pass

    def GetHeaders(self):
        return self.headers
