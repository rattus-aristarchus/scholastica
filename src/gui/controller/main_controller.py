#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 27 15:56:59 2022

@author: kryis
"""

import os

from kivy.logger import Logger
from kivy.clock import Clock

from gui.widgets import BasePopup, OpenFile, NewFile
from gui.tag_tree import TagNode, EntryNode, SourceNode
from gui.controller.keyboard_listener import KeyboardListener
import storage.tagfile as tagfile
import storage.sourcefile as sourcefile
from util import CONF
from util import STRINGS
import messaging.rpc as rpc

LANG = CONF["misc"]["language"]

#TODO: create a tree controller and separate all tree functions into that

class Controller:
    
    def __init__(self, view):
        self.view = view
        self.view.controller = self
        self.tag_file = None
        self.tag_nest = None
        
       # self.tree = view.ids["tree"]
        self.kbd_listener = KeyboardListener(view, self) 
        self.msgr = rpc.Messenger(self.view)
        self.msgr.start()
    
        #the copied tagnode; this is needed for the copy-paste functionality
        self.clipboard = None
        self._cut = False
        
    #    if not tag_file_path == None:
    #        self.open_file(tag_file_path)
    
    def _get_tree(self):
        return self.view.ids['tree']
    
    tree = property(fget=_get_tree)
    
    def new_file_popup(self):
        popup = NewFile(self)
        popup.open()
        
        
#        Logger.debug("The popup has the following children:")
 #       for child in popup.ids['filechooser'].children:
  #          self.print_children(child, 0)
        
    def print_children(self, widget, lvl):
        Logger.debug("lvl " + str(lvl) + ": " + str(widget))
        #Logger.debug("id: " + widget.id)
        for child in widget.children:
            self.print_children(child, lvl+1)
        
    def open_file_popup(self):
        OpenFile(self).open()
    
    def new_file(self, path):
        if os.path.exists(path):
            msg = STRINGS["error"][1][LANG][0] + \
                  path + \
                  STRINGS["error"][1][LANG][1]
            self.popup(msg)
        else:
            try:
                open(path, 'w').close()
                self.open_file(path)
            except OSError as e:
                #TODO: test specifically that this works 
                self.popup(e.strerror + "; " + e.filename)
            
    def open_file(self, path):
        if not self.tag_file == None:
            self.close_file()
        
        #First, open the file
        self.tag_file, messages = tagfile.read_tag_file(path)
        self.tag_nest = self.tag_file.tag_nest
        self.msgr.tag_file = self.tag_file
        self.tree.show(self.tag_file)
        if not len(messages) == 0:
            self.controller.popup("\n".join(messages))
        
    def close_file(self):
        self.tree.clear()
        self.msgr.tag_file = None
        self.tag_file = None
        self.tag_nest = None
    
    def save_file(self):
        tagfile.write_tag_file(self.tag_file)

    def popup(self, message, callback=None):
        Logger.info(f"Controller: popup created with message {message}")
        
        popup = BasePopup()
        popup.ids["label"].text = message
        popup.callback = callback
        popup.open()
            
    def return_kbd(self):
        self.kbd_listener.bind_keyboard() 