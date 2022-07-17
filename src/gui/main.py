#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun  4 19:36:01 2022

@author: kryis
"""

from kivy.logger import Logger
import kivy
from kivy.app import App
from kivy.clock import Clock

import util

from gui.widgets import View
from gui.controller.main_controller import Controller
from gui.controller.tag_tree_controller import TagTreeController

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

    def __init__(self, file_path=path_3):
        super().__init__()
        self.lang = LANG
        self.theme = THEME
        self.path = file_path

    def build(self):
        Logger.info("Main: building the app")

        self.title = "Scholastica"

        def set_title(title):
            self.title = title

        self.controller = Controller()
        self.controller.set_title = set_title
        self.view = View(self.controller)
        self.controller.set_view(self.view)
        self.controller.open_file(self.path)

        return self.view
