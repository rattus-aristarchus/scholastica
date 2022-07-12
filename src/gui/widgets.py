#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 27 13:44:51 2022

@author: kryis
"""

import os

from kivy.logger import Logger
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

from util import CONF
from util import STRINGS
import messaging.rpc as rpc

LANG = CONF["misc"]["language"]

class View(BoxLayout):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.controller = None
    
#TODO: cancel button

class BasePopup(Popup):    
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.callback = None
    
    def enter(self):
        self.ok()
    
    def escape(self):
        self.dismiss()
        
    def ok(self):
        if not self.callback == None:
            self.callback()
        self.dismiss()
      
class FilePopup(Popup):
    
    def __init__(self, controller, **kwargs):
        super().__init__(**kwargs)
        self.controller = controller
        
        #I have found no simple way to change the text of labels inside the 
        #file picker into different
        #languages; the following monstrosity takes care of that
        for child in self.ids['filechooser'].children[0].children[0].children:
            if isinstance(child, BoxLayout):
                for child_1 in child.children:
                    if isinstance(child_1, Label) and child_1.text == "Name":
                        child_1.text = STRINGS["file_picker"][5][LANG]
                    if isinstance(child_1, Label) and child_1.text == "Size":
                        child_1.text = STRINGS["file_picker"][6][LANG]
      
    def close(self):
        self.dismiss()
        
      
class OpenFile(FilePopup):
        
    def act(self, directory, filename):
        self.dismiss()
        if not self.controller == None:
            path = os.path.join(directory, filename)
            self.controller.open_file(path)
        
class NewFile(FilePopup):
        
    def act(self, directory, filename):
        self.dismiss()
        if not self.controller == None:
            path = os.path.join(directory, filename)
            self.controller.new_file(path)
        