#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 23 19:08:19 2022

@author: kryis
"""

import logging
import storage.tagfile as tagfile
import gui.main as gui

#TODO: message level doesn't seem to be affected by this
logging.basicConfig(level=logging.DEBUG)
address = "/media/kryis/TOSHIBA EXT/записи/организатор записей/тестовый файл.txt"
address_1 = "/media/kryis/TOSHIBA EXT/записи/погреб/описание мира/планета и ее биосфера/планетология.sca"
address_2 = "/media/kryis/TOSHIBA EXT/наука/схоластика/капитализм.sca"
file = tagfile.read_tag_file(address_2)
app = gui.Main(file)
app.run()
