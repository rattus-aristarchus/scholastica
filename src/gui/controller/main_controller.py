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
from gui.controller.tag_tree_controller import TagTreeController
import storage.tagfile as tagfile
import storage.sourcefile as sourcefile
from util import CONF
from util import STRINGS
import messaging.rpc as rpc

LANG = CONF["misc"]["language"]


class Controller:

    def __init__(self):
        self.tree_controller = TagTreeController(self)
        self.kbd_listener = KeyboardListener(self, self.tree_controller)
        self.msgr = rpc.Messenger()
        self.msgr.start()

        self.tag_file = None
        self.tag_nest = None

    def set_view(self, view):
        self.view = view
        self.tree_controller.set_view(view)
        self.kbd_listener.set_view(view)
        self.msgr.set_view(view)

    @property
    def tree(self):
        return self.view.ids['tree']

    def new_file_popup(self):
        popup = NewFile(self)
        popup.open()

    def open_file_popup(self):
        OpenFile(self).open()

    def new_file(self, path):
        path = path + CONF["misc"]["extension"]

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
                # TODO: test specifically that this works
                self.popup(e.strerror + "; " + e.filename)

    def open_file(self, path):
        if self.tag_file is not None:
            self.close_file()

        # First, open the file
        self.tag_file, messages = tagfile.read_tag_file(path)
        self.tag_nest = self.tag_file.tag_nest
        self.msgr.tag_file = self.tag_file
        self.tree_controller.tag_file = self.tag_file
        self.tree_controller.tag_nest = self.tag_nest
        self.tree.show(self.tag_file)
        if not len(messages) == 0:
            self.popup("\n".join(messages))

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
