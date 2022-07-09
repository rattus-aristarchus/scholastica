#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun  4 19:36:01 2022

@author: kryis
"""

from kivy.logger import Logger
import kivy
kivy.require('2.1.0') # replace with your current kivy version !
from kivy.app import App
from kivy.clock import Clock

import storage.tagfile as tagfile
import messaging.rpc as rpc
import util

from gui.widgets import View
from gui.keyboard_listener import KeyboardListener
from gui.controller import Controller

#logger = logging.getLogger(__name__)
#logging.basicConfig(level=logging.DEBUG)

STRINGS = util.STRINGS
CONF = util.CONF
LANG = CONF["misc"]["language"]

class Main(App):

    def __init__(self):
        super().__init__()

    def build(self):
        Logger.info("Main: building the app")
        
        address = "/media/kryis/TOSHIBA EXT/записи/организатор записей/тестовый файл.txt"
        address_1 = "/media/kryis/TOSHIBA EXT/записи/погреб/описание мира/планета и ее биосфера/планетология.sca"
        address_2 = "/media/kryis/TOSHIBA EXT/наука/схоластика/капитализм.sca"
        self.tag_file, messages = tagfile.read_tag_file(address_2)
        
        self.title = "Scholastica"    
        self.view = View()
        tree = self.view.ids['tree']
        
        
        msgr = rpc.Messenger(self.tag_file, self.view)
        msgr.start()
        self.controller = Controller(tag_file=self.tag_file, 
                                     view=self.view,
                                     msgr=msgr,
                                     return_kbd=self.return_kbd)
        self.kbd_listener = KeyboardListener(tree, self.controller)
        tree.controller = self.controller
        tree.show(self.tag_file)
        

        def tell_user(dt, messages): 
            self.controller.popup("\n".join(messages))
        
        if not len(messages) == 0:
            Clock.schedule_once(lambda dt: tell_user(dt, messages), 0.5)
            
        return self.view       
    
    def return_kbd(self):
        self.kbd_listener.bind_keyboard()
        
