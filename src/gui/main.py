#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun  4 19:36:01 2022

@author: kryis
"""

import logging
import kivy
kivy.require('2.1.0') # replace with your current kivy version !
from kivy.app import App
from kivy.clock import mainthread

from gui.widgets import View
from gui.keyboard_listener import KeyboardListener
from gui.controller import Controller

import storage.tagfile as tagfile
import storage.sourcefile as sourcefile
import messaging.rpc as rpc
import util

logger = logging.getLogger(__name__)
STRINGS = util.STRINGS
CONF = util.CONF
LANG = CONF["misc"]["language"]

class Main(App):

    def __init__(self, tag_file):
        super().__init__()
        self.tag_file = tag_file
        self.title = "Scholastica"        
        
    def listen(self):
        msgr = rpc.Messenger(self.file_saved, 
                             self.query_tags,
                             self.query_sources)
        msgr.start()

    def build(self):
        self.view = View()
        tree = self.view.ids['tree']
        self.controller = Controller(self.tag_file, 
                                     self.view,
                                     self.return_kbd)
        self.kbd_listener = KeyboardListener(tree, self.controller)
        tree.controller = self.controller
        tree.show(self.tag_file.tag_nest)
        return self.view       
    
    def return_kbd(self):
        self.kbd_listener.bind_keyboard()

    #TODO: move these functions to the messenger
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
        sourcefile.clean(file)
        self.tag_file.source_files.remove(file)
        tagfile.write_tag_file(self.tag_file)
        
    @mainthread
    def add_file(self, file):
        self.view.ids['tree'].add_all_from(file)
        self.tag_file.source_files.append(file)
        tagfile.write_tag_file(self.tag_file)

