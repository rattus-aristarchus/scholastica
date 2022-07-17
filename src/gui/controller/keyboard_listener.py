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

# TODO: some key combination should delete nodes recursively


class KeyboardListener(Widget):
    
    def __init__(self, main_controller, tree_controller, **kwargs):
        super().__init__(**kwargs)
        self._keyboard = None
        self.bind_keyboard()
        self.controller = main_controller
        self.tree_controller = tree_controller

    def set_view(self, view):
        self.view = view

    def bind_keyboard(self):
        self._keyboard = Window.request_keyboard(
            self.close_keyboard, self, 'text')
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

    def close_keyboard(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None
    
    """
    This is called when a key is pressed.
    """
    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        logger.debug('The key', keycode, 'have been pressed')
        logger.debug(' - text is %r' % text)
        logger.debug(' - modifiers are %r' % modifiers)
        
        tree = self.view.ids['tree']
        key = keycode[1]
        ctrl = 'ctrl' in modifiers
        shift = 'shift' in modifiers
        alt = 'alt' in modifiers
        
        # Keycode is composed of an integer + a string
        # If we hit escape, release the keyboard
        if key == 'escape':            
            root = App.get_running_app().root_window.children[0]
            if isinstance(root, BasePopup):
                root.escape()
        elif key == 'up':
            if ctrl and shift:
                self.tree_controller.push_node(forward=False)
            elif ctrl:
                tree.step_up_over()
            else:
                tree.step_up()                
        elif key == 'down':
            if ctrl and shift:
                self.tree_controller.push_node(forward=True)
            elif ctrl:
                tree.step_down_over()
            else:
                tree.step_down()
        elif key == 'left':
            tree.step_out()
        elif key == 'right':
            tree.step_in()
        elif key == 'enter':
            root = App.get_running_app().root_window.children[0]
            if isinstance(root, BasePopup):
                root.enter()
            else:
                self.tree_controller.enter()
        elif key == 'delete':
            if shift:
                self.tree_controller.delete_recursively_message()
            else:
                self.tree_controller.edit_node(from_end=False)
        elif key == 'backspace':
            self.tree_controller.edit_node(from_end=True)
        elif key == 'tab':
            if ctrl and not alt:
                self.tree_controller.raise_selected_node()
            elif not alt:
                self.tree_controller.lower_selected_node()
        elif key == 'c' and ctrl:
            self.tree_controller.copy()
        elif key == 'с' and ctrl:
            self.tree_controller.copy()
        elif key == 'x' and ctrl:
            self.tree_controller.cut()
        elif key == 'ч' and ctrl:
            self.tree_controller.cut()
        elif key == 'v' and ctrl:
            self.tree_controller.paste()
        elif key == 'м' and ctrl:
            self.tree_controller.paste()
            
        # Return True to accept the key. Otherwise, it will be used by
        # the system.
        return True
