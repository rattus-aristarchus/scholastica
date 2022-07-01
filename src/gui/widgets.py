#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 27 13:44:51 2022

@author: kryis
"""

from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout

class View(BoxLayout):
    pass   

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