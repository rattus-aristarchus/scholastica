#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 23 19:08:19 2022

@author: kryis
"""

import sys
from kivy.logger import Logger, LOG_LEVELS
from kivy.config import Config

from util import CONF, LOGS_DIR
Logger.setLevel(LOG_LEVELS[CONF['misc']['log_level']])
Config.set('kivy', 'log_dir', LOGS_DIR)
import gui.main as gui
import converter.converter as converter

Logger.info("Starting application with arguments " + str(sys.argv))

convert = True


if convert:
    app = converter.Converter(0)
elif len(sys.argv) > 1:
    app = gui.Main(sys.argv[1])
else:
    app = gui.Main()

app.run()
