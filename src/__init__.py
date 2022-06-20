#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 23 19:08:19 2022

@author: kryis
"""


import storage.tagfile as tagfile
import storage.sourcefile as sourcefile
import data
import gui.main as gui

address = "/media/kryis/TOSHIBA EXT/записи/организатор записей/тестовый файл.txt"
address_1 = "/media/kryis/TOSHIBA EXT/записи/погреб/описание мира/планета и ее биосфера/планетология.sca"
file = tagfile.read_tag_file(address)
app = gui.Main(file)
app.listen()
app.run()