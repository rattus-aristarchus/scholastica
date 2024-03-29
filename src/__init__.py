#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 23 19:08:19 2022

@author: kryis
"""

import sys
from kivy.logger import Logger, LOG_LEVELS
from kivy.config import Config
import util
from util import CONF
Logger.setLevel(LOG_LEVELS[CONF['misc']['log_level']])
Config.set('kivy', 'log_dir', util.LOGS_DIR)
import gui.main as gui

Logger.info("Starting application with arguments " + str(sys.argv))

if len(sys.argv) > 1:
    app = gui.Main(sys.argv[1])
else:
    app = gui.Main()

app.run()
