#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 23 19:08:19 2022

@author: kryis
"""

import logging
from util import CONF
import storage.tagfile as tagfile
import gui.main as gui

logging.basicConfig(level=logging.INFO)
address = "/media/kryis/TOSHIBA EXT/записи/организатор записей/тестовый файл.txt"
address_1 = "/media/kryis/TOSHIBA EXT/записи/погреб/описание мира/планета и ее биосфера/планетология.sca"
file = tagfile.read_tag_file(address)
app = gui.Main(file)
app.listen()
app.run()
