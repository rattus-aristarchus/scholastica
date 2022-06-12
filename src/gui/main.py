#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun  4 19:36:01 2022

@author: kryis
"""

import kivy
kivy.require('2.1.0') # replace with your current kivy version !
from kivy.app import App
from kivy.base import runTouchApp
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView

from gui.tag_tree import TagTree
import storage.tagfile as tagfile
import storage.sourcefile as sourcefile

    
class Main(App):

    def __init__(self, tag_file):
        super().__init__()
        self.tag_file = tag_file
        self.title = "Scholastica"


    def build(self):
        self.view = View()
        tree = self.view.ids['tree']
        tree.file_callback(self.save_file)
        tree.edit_callback(self.edit_tag)
        tree.scroll_callback(self.scroll)
        self.view.show(self.tag_file.tag_nest)
        return self.view


    def save_file(self):
        tagfile.write_tag_file(self.tag_file)
        
        
    def edit_tag(self, old_name, new_name):
        for source_file in self.tag_file.source_files:
            sourcefile.edit_tag(old_name, new_name, source_file)        
        
    def scroll(self, widget):
        if self.view.ids['tree'].size[1] > self.view.ids['scroll'].size[1]:
            self.view.ids['scroll'].scroll_to(widget)


class View(BoxLayout):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        #This class acts as a keyboard listener
        self.bind_keyboard()
        self.ids['tree'].kbd_callback(self.bind_keyboard)
        
    def bind_keyboard(self):
        self._keyboard = Window.request_keyboard(
            self._keyboard_closed, self, 'text')
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
    
    
    def show(self, tag_nest):
        """
        This displays a tree of tags
        """
        tree = self.ids['tree']
        tree.show(tag_nest)
    
    
    def _keyboard_closed(self):
        print('My keyboard has been closed!')
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None
    
    """
    This is called when a key is pressed.
    """
    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
   #     print('The key', keycode, 'have been pressed')
   #     print(' - text is %r' % text)
   #     print(' - modifiers are %r' % modifiers)
        
        tree = self.ids['tree']
                
        # Keycode is composed of an integer + a string
        # If we hit escape, release the keyboard
        if keycode[1] == 'escape':
            keyboard.release()
        elif keycode[1] == 'up':
            if len(modifiers) == 0:
                tree.step_up()
            elif modifiers[0] == 'ctrl':
                tree.step_up_over()
        elif keycode[1] == 'down':
            if len(modifiers) == 0:
                tree.step_down()
            elif modifiers[0] == 'ctrl':
                tree.step_down_over()
        elif keycode[1] == 'down':
            tree.step_down()
        elif keycode[1] == 'left':
            tree.step_out()
        elif keycode[1] == 'right':
            tree.step_in()
        elif keycode[1] == 'enter':
            tree.enter()
        elif keycode[1] == 'delete':
            tree.edit(False)
        elif keycode[1] == 'backspace':
            tree.edit(True)
        elif keycode[1] == 'c':
            if len(modifiers) > 0 and modifiers[0] == 'ctrl':
                tree.copy()
        elif keycode[1] == 'v' and modifiers[0] == 'ctrl':
            if len(modifiers) > 0 and modifiers[0] == 'ctrl':
                tree.paste()
#        elif keycode[1] == 'pagedown':
 #           tree.test_scroll()
            
        # Return True to accept the key. Otherwise, it will be used by
        # the system.
        return True

#class KeyboardListener(Widget):