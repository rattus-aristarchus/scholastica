#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 13 15:39:42 2022

@author: kryis
"""
import logging
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.app import App

import gui.main as main
from gui.widgets import BasePopup

logger = logging.getLogger(__name__)

#TODO: some key combination should delete nodes recursively
class KeyboardListener(Widget):
    
    def __init__(self, tree, controller, **kwargs):
        super().__init__(**kwargs)
        self.bind_keyboard()
        self.tree = tree
        self.controller = controller
        
    def bind_keyboard(self):
        self._keyboard = Window.request_keyboard(
            self._keyboard_closed, self, 'text')
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
  
    
    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None
    
    """
    This is called when a key is pressed.
    """
    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        logger.debug('The key', keycode, 'have been pressed')
        logger.debug(' - text is %r' % text)
        logger.debug(' - modifiers are %r' % modifiers)
        
        key = keycode[1]
        ctrl = len(modifiers) > 0 and modifiers[0] == 'ctrl'
        shift = len(modifiers) > 0 and modifiers[0] == 'shift'
        alt = len(modifiers) > 0 and modifiers[0] == 'alt'
        
        # Keycode is composed of an integer + a string
        # If we hit escape, release the keyboard
        if key == 'escape':            
            root = App.get_running_app().root_window.children[0]
            if isinstance(root, BasePopup):
                root.escape()
        elif key == 'up':
            if ctrl:
                self.tree.step_up_over()
            else:
                self.tree.step_up()                
        elif key == 'down':
            if ctrl:
                self.tree.step_down_over()
            else:
                self.tree.step_down()
        elif key == 'down':
            self.tree.step_down()
        elif key == 'left':
            self.tree.step_out()
        elif key == 'right':
            self.tree.step_in()
        elif key == 'enter':
            root = App.get_running_app().root_window.children[0]
            if isinstance(root, BasePopup):
                root.enter()
            else:
                self.controller.enter()
        elif key == 'delete':
            if shift:
                self.controller.delete_recursively_message()
            else:
                self.controller.edit_node(False)
        elif key == 'backspace':
            self.controller.edit_node(True)
        elif key == 'tab':
            if ctrl and not alt:
                self.controller.raise_selected_node()
            elif not alt:
                self.controller.lower_selected_node()
        elif key == 'c' and ctrl:
            self.controller.copy()
        elif key == 'с' and ctrl:
            self.controller.copy()
        elif key == 'x' and ctrl:
            self.controller.cut()
        elif key == 'ч' and ctrl:
            self.controller.cut()
        elif key == 'v' and ctrl:
            self.controller.paste()
        elif key == 'м' and ctrl:
            self.controller.paste()
            
        # Return True to accept the key. Otherwise, it will be used by
        # the system.
        return True