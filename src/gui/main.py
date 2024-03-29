#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun  4 19:36:01 2022

@author: kryis
"""


import kivy
from kivy.logger import Logger
from kivy.app import App
from kivy.base import ExceptionHandler, ExceptionManager

import util

from gui.widgets import View
from gui.controller.main_controller import Controller

kivy.require('2.1.0')  # replace with your current kivy version !

STRINGS = util.STRINGS
CONF = util.CONF
LANG = CONF["misc"]["language"]
THEME = CONF["misc"]["theme"]

path = "/media/kryis/TOSHIBA EXT/записи/организатор записей/тестовый файл.scla"
path_1 = "/media/kryis/TOSHIBA EXT/записи/погреб/описание мира/планета и ее биосфера/планетология.scla"
path_2 = "/media/kryis/TOSHIBA EXT/наука/схоластика/капитализм.scla"
path_3 = "/media/kryis/TOSHIBA EXT/наука/схоластика/гендер.scla"


class Main(App):

    def __init__(self, file_path=None):
        super().__init__()
        self.lang = LANG
        self.theme = THEME
        if file_path is None:
            self.path = CONF['misc']['last_file']
        else:
            self.path = file_path

    def build(self):
        Logger.info("Main: building the app")

        self.title = STRINGS['misc'][0][LANG]

        def set_title(title):
            self.title = title

        self.controller = Controller(self)
        self.controller.set_title = set_title
        self.view = View(self.controller)
        self.controller.set_view(self.view)
        ExceptionManager.add_handler(Handler(self.controller))
        if self.path is not None:
            self.controller.open_file(self.path)

        return self.view

    def on_start(self):
        util.start_profiling()
        pass

    def on_stop(self):
        util.end_profiling()
        self.controller.msgr.stop()


class Handler(ExceptionHandler):

    def __init__(self, controller):
        super().__init__()
        self.controller = controller

    def handle_exception(self, inst):
        self.controller.popup(STRINGS['popup'][12][LANG] + util.LOGS_DIR)
        Logger.exception(str(inst))
        return ExceptionManager.PASS
