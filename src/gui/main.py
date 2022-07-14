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


class Main(App):

    def __init__(self):
        super().__init__()
        self.lang = LANG
        self.theme = THEME

    def build(self):
        Logger.info("Main: building the app")

        self.title = "Scholastica"
        self.view = View()

        address = "/media/kryis/TOSHIBA EXT/записи/организатор записей/тестовый файл.txt"
        address_1 = "/media/kryis/TOSHIBA EXT/записи/погреб/описание мира/планета и ее биосфера/планетология.sca"
        address_2 = "/media/kryis/TOSHIBA EXT/наука/схоластика/капитализм.sca"

        # since the interface hasn't been initialized yet we've got to delay
        # settingg the controller for the tree
        def set_tree_controller(dt):
            tree = self.view.ids['tree']
            self.controller = Controller(self.view)
            tree.main_controller = self.controller
            self.controller.open_file(address)

        Clock.schedule_once(set_tree_controller, 5)

        return self.view
