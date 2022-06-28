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

from gui.widgets import View
from gui.keyboard_listener import KeyboardListener
from gui.controller import Controller

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
        

    def build(self):
        self.view = View()
        tree = self.view.ids['tree']
        self.controller = Controller(self.tag_file, 
                                     self.view,
                                     self.return_kbd)
        self.kbd_listener = KeyboardListener(tree, self.controller)
        tree.controller = self.controller
        tree.show(self.tag_file.tag_nest)
        
        msgr = rpc.Messenger(self.tag_file, self.view)
        msgr.start()
        return self.view       
    
    def return_kbd(self):
        self.kbd_listener.bind_keyboard()