#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 27 15:56:59 2022

@author: kryis
"""

import os

from kivy.logger import Logger
from kivy.clock import Clock

import util
from util import CONF, STRINGS
from gui.widgets import BasePopup, OpenFile, NewFile
from gui.controller.keyboard_listener import KeyboardListener
from gui.controller.tag_tree_controller import TagTreeController
import storage.tagfile as tagfile
import messaging.rpc as rpc

LANG = CONF['misc']['language']


class Controller:

    def __init__(self, app):
        self.app = app
        self.tree_controller = TagTreeController(self)
        self.kbd_listener = KeyboardListener(self, self.tree_controller)
        self.msgr = rpc.Messenger()
        self.msgr.start()

        self.tag_file = None
        self.tag_nest = None

    def quit(self):
        self.app.stop()

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
        self._check_default_location()
        popup.set_path(CONF['misc']['default_location'])
        popup.open()

    def open_file_popup(self):
        popup = OpenFile(self)
        self._check_default_location()
        popup.set_path(CONF['misc']['default_location'])
        popup.open()

    def _check_default_location(self):
        if CONF['misc']['default_location'] is None:
            util.set_conf('misc', 'default_location', util.MAIN_DIR)

    def new_file(self, path):
        path = path + CONF['misc']['extension']

        if os.path.exists(path):
            msg = STRINGS['error'][1][LANG][0] + \
                  path + \
                  STRINGS['error'][1][LANG][1]
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
        if not len(messages) == 0:
            Clock.schedule_once(lambda dt: self.popup("\n".join(messages)), 0.5)
        self.tag_nest = self.tag_file.tag_nest
        self.msgr.tag_file = self.tag_file
        self.tree_controller.tag_file = self.tag_file
        self.tree_controller.tag_nest = self.tag_nest
        self.tree.show(self.tag_file)

        # if the file is empty, we have to show a hint; if it isn't, we have to hide it
        if len(self.tag_file.tag_nest.tags) > 0:
            self.view.hide_hint()
        else:
            self.view.show_hint()

        # without the next line, when you create a new file the keyboard listener dies and
        # doesn't revive for any next file; although when you just open a new file it works
        # fine. can't for the life of me understand why
        self.kbd_listener.bind_keyboard()
        self.set_title(os.path.basename(path))

        # change the default location for opening files
        util.set_conf('misc', 'default_location', os.path.dirname(path))
        util.set_conf('misc', 'last_file', path)

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

    def change_language(self):
        if LANG == 'ru':
            util.set_conf('misc', 'language', 'en')
        elif LANG == 'en':
            util.set_conf('misc', 'language', 'ru')
        self.popup(STRINGS['popup'][11][LANG])

    def hide_tutorial(self):
        self.hide_tutorial()
        util.set_conf('misc', 'show_tutorial', False)

    def show_tutorial(self):
        self.view.show_tutorial()
        util.set_conf('misc', 'show_tutorial', True)

    def toggle_tutorial(self):
        if CONF['misc']['show_tutorial']:
            self.hide_tutorial()
        else:
            self.show_tutorial()

    def enter(self):
        if self.view.hint_shown:
            self.view.hide_hint()
