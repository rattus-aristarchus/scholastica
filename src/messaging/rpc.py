#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 17 15:51:26 2022

@author: kryis

This module passes messages from scholastica plugins for text editors to the
main application.
"""

#import logging

from kivy.logger import Logger
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.client import ServerProxy
import threading
from kivy.clock import mainthread

import storage.tagfile as tagfile
import storage.sourcefile as sourcefile

#logger = logging.getLogger(__name__)

class Messenger(threading.Thread):
    
    def __init__(self, tag_file, view):
        super().__init__()
        self.tag_file = tag_file
        self.view = view
        self.server = SimpleXMLRPCServer(('localhost', 9000), 
                                         logRequests=True,
                                         allow_none=True)
        self.server.register_function(self.update_file, 'update_file')
        self.server.register_function(self.query_tags, 'query_tags')
        self.server.register_function(self.query_sources, 'query_sources')
        self.proxy = ServerProxy('http://localhost:8000', allow_none=True)
        
    def run(self):
        try:
            Logger.info("Messenger is listening...")
            self.server.serve_forever()
        except KeyboardInterrupt:
            Logger.info("Messenger is exiting")
            
    def query_tags(self):
        Logger.info("Messenger: query_tags")
        
        result = []
        for tag in self.tag_file.tag_nest.tags:
            result.append(tag.text)
        return result
     
    def query_sources(self, path):
        Logger.info(f"Messenger: query sources for path {path}")
        
        result = []
        for source_file in self.tag_file.source_files:
            if source_file.address == path:
                for source in source_file.sources:
                    result.append(source.text)
                break
        return result
   
    #Activated when the plugin has registered that a file has been saved
    def update_file(self, path):
        Logger.info(f"Messenger: update received for file {path}")
        try:
            #First, we check if the file is one of those already tracked by the 
            #application. If it is, all its content is reloaded.
            existing_file = None
            for check in self.tag_file.source_files:
                if check.address == path:
                    existing_file = check
                    break
                    
            if not existing_file == None:
                #If it is already tracked:   
                self.replace_existing(existing_file, path)
            else:
                #If it isn't, we read the file and see if it has any tags at all. 
                #If it doesn't, there is no point in adding it
                self.add_new(path)
            return ""
        except Exception as err:
            Logger.error(f"Unexpected {err=}, {type(err)=}")
    
    @mainthread
    def replace_existing(self, old_file, new_path):
        Logger.info("Messenger: file already exists. Removing old file.")
        
        self.view.ids['tree'].remove_all_from(old_file)        
        self.tag_file.remove_file(old_file)
        
        new_file, messages = sourcefile.read(new_path, self.tag_file.tag_nest)
        self.view.ids['tree'].add_all_from(new_file)
        self.tag_file.add_file(new_file)
        tagfile.write_tag_file(self.tag_file)
    
    @mainthread
    def add_new(self, path):        
        Logger.info("Messenger: the file is new. Adding it.")
        
        new_file, messages = sourcefile.read(path, self.tag_file.tag_nest)
        self.view.ids['tree'].add_all_from(new_file)
        self.tag_file.add_file(new_file)
        tagfile.write_tag_file(self.tag_file)    
        
        
    """
    Send a message to the plugin to open a file located at path and scroll to
    the piece of text in item.
    
    path, item - strings.
    """
    def open_file(self, path, item):
        Logger.info(f"Messenger: opening file {path} at item {item}")

        try:        
            response = self.proxy.open_file(path, item)
            Logger.info(response)
        except ConnectionRefusedError:
            Logger.warning("Messenger: connection to the text editor plugin " \
                           + "refused, most likely because it is"\
                           + " not currently running")
        
            