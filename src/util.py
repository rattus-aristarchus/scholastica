#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 20 16:06:49 2022

@author: kryis
"""

import yaml
import os
import sys
from kivy.logger import Logger

# getcwd returns the current working directory, which can change during program execution,
# and which can give different results depending on where the program is launched from. for
# now, sys.path[0] is a better alternative, it gives the initial directory from which the script was launched

# MAIN_DIR = os.path.dirname(os.getcwd())
MAIN_DIR = os.path.dirname(sys.path[0])
Logger.info("Util: using dir " + MAIN_DIR)

CONF = yaml.safe_load(open(MAIN_DIR + "/conf.yml", "r"))
STRINGS = yaml.safe_load(open(MAIN_DIR + "/strings.yml", "r"))
