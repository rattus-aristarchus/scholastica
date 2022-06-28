#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 17 15:51:26 2022

@author: kryis

This module passes messages from scholastica plugins for text editors to the
main application.
"""

import logging
from xmlrpc.server import SimpleXMLRPCServer
import threading
from kivy.clock import mainthread

import storage.tagfile as tagfile
import storage.sourcefile as sourcefile

logger = logging.getLogger(__name__)

class Messenger(threading.Thread):
    
    def __init__(self, tag_file, view):
        super().__init__()
        self.tag_file = tag_file
        self.view = view
        self.server = SimpleXMLRPCServer(('localhost', 9000), logRequests=True)
        self.server.register_function(self.file_saved, 'on_save')
        self.server.register_function(self.query_tags, 'query_tags')
        self.server.register_function(self.query_sources, 'query_sources')
        
    def run(self):
        try:
            logger.info("Messenger is listening...")
            self.server.serve_forever()
        except KeyboardInterrupt:
            logger.info("Messenger is exiting")
            
    def query_tags(self):
         result = []
         for tag in self.tag_file.tag_nest.tags:
             result.append(tag.text)
         return result
     
    def query_sources(self, path):
        logger.info(f"QUERY SOURCES: for path {path}")
        result = []
        for source_file in self.tag_file.source_files:
            if source_file.address == path:
                for source in source_file.sources:
                    result.append(source.text)
                break
        return result
   
    #Activated when the plugin has registered that a file has been saved
    def file_saved(self, path):
        logger.info("FILE SAVED")
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
                self.remove_file(existing_file)
                new_file = sourcefile.read(path, self.tag_file.tag_nest)
                if len(new_file.tags) > 0:
                    self.add_file(new_file)
            else:
                #If it isn't, we read the file and see if it has any tags at all. 
                #If it doesn't, there is no point in adding it
                new_file = sourcefile.read(path, self.tag_file.tag_nest)
                if len(new_file.tags) > 0:
                    self.add_file(new_file)
            return ""
        except Exception as err:
            logger.error(f"Unexpected {err=}, {type(err)=}")
   
    @mainthread
    def remove_file(self, file):    
        self.view.ids['tree'].remove_all_from(file)
        sourcefile.clean(file, self.tag_file.tag_nest)
        self.tag_file.source_files.remove(file)
        tagfile.write_tag_file(self.tag_file)
        
    @mainthread
    def add_file(self, file):
        self.view.ids['tree'].add_all_from(file)
        self.tag_file.source_files.append(file)
        tagfile.write_tag_file(self.tag_file)