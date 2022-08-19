#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 20 16:06:49 2022

@author: kryis
"""

import yaml
import os
import sys
import shutil
from kivy.logger import Logger

# getcwd returns the current working directory, which can change during program execution,
# and which can give different results depending on where the program is launched from. for
# now, sys.path[0] is a better alternative, it gives the initial directory from which the script was launched

# MAIN_DIR = os.path.dirname(os.getcwd())
MAIN_DIR = os.path.dirname(sys.path[0])
CONF_PATH = os.path.join(MAIN_DIR, "conf.yml")
DEFAULT_CONF_PATH = os.path.join(MAIN_DIR, "default_conf.yml")
CONST_PATH = os.path.join(MAIN_DIR, "const.yml")
STRINGS_PATH = os.path.join(MAIN_DIR, "strings.yml")

if not os.path.exists(CONF_PATH):
    # TODO: maybe this has to check that the file is complete
    shutil.copy(DEFAULT_CONF_PATH, CONF_PATH)

CONF = yaml.safe_load(open(CONF_PATH, "r", encoding="utf-8"))
CONST = yaml.safe_load(open(CONST_PATH, "r", encoding="utf-8"))
STRINGS = yaml.safe_load(open(STRINGS_PATH, "r", encoding="utf-8"))


def set_conf(category, name, value):
    CONF[category][name] = value
    with open(CONF_PATH, "w", encoding="utf-8") as file:
        yaml.dump(CONF, file)
