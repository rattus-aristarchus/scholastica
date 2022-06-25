#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 17 15:51:26 2022

@author: kryis
"""

from xmlrpc.server import SimpleXMLRPCServer
import threading

class Messenger(threading.Thread):
    
    def __init__(self, on_save, query_tags, query_sources):
        super().__init__()
        self.server = SimpleXMLRPCServer(('localhost', 9000), logRequests=True)
        self.server.register_function(on_save, 'on_save')
        self.server.register_function(query_tags, 'query_tags')
        self.server.register_function(query_sources, 'query_sources')
        
    def run(self):
        try:
            print("listening...")
            self.server.serve_forever()
        except KeyboardInterrupt:
            print("exiting...")