#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 27 15:56:59 2022

@author: kryis
"""


import zerorpc

class Listener(object):
    def say(self, msg):
        print(msg)
        return "heard you"

s = zerorpc.Server(Listener())
s.bind("tcp://0.0.0.0:4242")
s.run()