#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 20 16:06:49 2022

@author: kryis
"""

import cProfile
import pstats
import io
import yaml
import os
import sys
import shutil
from kivy.logger import Logger
from kivy.clock import Clock

# getcwd returns the current working directory, which can change during program execution,
# and which can give different results depending on where the program is launched from. for
# now, sys.path[0] is a better alternative, it gives the initial directory from which the script was launched

# MAIN_DIR = os.path.dirname(os.getcwd())
MAIN_DIR = os.path.dirname(sys.path[0])
DEFAULT_CONF_PATH = os.path.join(MAIN_DIR, "default_conf.yml")
CONST_PATH = os.path.join(MAIN_DIR, "const.yml")
STRINGS_PATH = os.path.join(MAIN_DIR, "strings.yml")

user_dir = os.path.expanduser("~")
DOCS_DIR = os.path.join(user_dir, "scholastica")
CONF_PATH = os.path.join(DOCS_DIR, "conf.yml")
LOGS_DIR = os.path.join(DOCS_DIR, "logs")
LOGS_FILE = "last_log.txt"
LOGS_PATH = os.path.join(LOGS_DIR, LOGS_FILE)
PROFILE_DUMP = os.path.join(LOGS_DIR, "profile_dump.txt")

if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

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

def add_to(category, name, value):
    if isinstance(CONF[category][name], list) and value in CONF[category][name]:
        CONF[category][name].remove(value)
        set_conf(category, name, CONF[category][name])

def remove_from(category, name, value):
    if isinstance(CONF[category][name], list) and value in CONF[category][name]:
        CONF[category][name].remove(value)
        set_conf(category, name, CONF[category][name])

profile = cProfile.Profile()


def start_profiling():
    profile.enable()


def end_profiling():
    profile.disable()
    result = io.StringIO()
    stats = pstats.Stats(profile, stream=result)
    stats.sort_stats(pstats.SortKey.CUMULATIVE).print_stats()
    if os.path.exists(PROFILE_DUMP):
        os.remove(PROFILE_DUMP)
    with open(PROFILE_DUMP, "w+") as file:
        file.write(result.getvalue())
