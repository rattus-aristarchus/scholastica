#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 23 19:08:19 2022

@author: kryis
"""

from kivy.logger import Logger, LOG_LEVELS
import gui.main as gui

Logger.setLevel(LOG_LEVELS['warning'])
app = gui.Main()
app.run()