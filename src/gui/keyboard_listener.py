#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 13 15:39:42 2022

@author: kryis
"""

from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.app import App

import gui.main as main

class KeyboardListener(Widget):
    
    def __init__(self, tree, **kwargs):
        super().__init__(**kwargs)
        self.bind_keyboard()
        self.tree = tree
        
    def bind_keyboard(self):
        self._keyboard = Window.request_keyboard(
            self._keyboard_closed, self, 'text')
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
  
    
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
        
        tree = self.tree
        key = keycode[1]
        ctrl = len(modifiers) > 0 and modifiers[0] == 'ctrl'
        
        # Keycode is composed of an integer + a string
        # If we hit escape, release the keyboard
        if key == 'escape':            
            root = App.get_running_app().root_window.children[0]
            if isinstance(root, main.BasePopup):
                root.escape()
        elif key == 'up':
            if ctrl:
                tree.step_up_over()
            else:
                tree.step_up()                
        elif key == 'down':
            if ctrl:
                tree.step_down_over()
            else:
                tree.step_down()
        elif key == 'down':
            tree.step_down()
        elif key == 'left':
            tree.step_out()
        elif key == 'right':
            tree.step_in()
        elif key == 'enter':
            root = App.get_running_app().root_window.children[0]
            if isinstance(root, main.BasePopup):
                root.enter()
            else:
                tree.enter()
        elif key == 'delete':
            tree.edit(False)
        elif key == 'backspace':
            tree.edit(True)
        elif key == 'tab':
            if ctrl:
                tree.ctrl_tab()
            else:
                tree.tab()
        elif key == 'c' and ctrl:
            tree.copy()
        elif key == 'с' and ctrl:
            tree.copy()
        elif key == 'x' and ctrl:
            tree.cut()
        elif key == 'ч' and ctrl:
            tree.cut()
        elif key == 'v' and ctrl:
            tree.paste()
        elif key == 'м' and ctrl:
            tree.paste()
            
        # Return True to accept the key. Otherwise, it will be used by
        # the system.
        return True