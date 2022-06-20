#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 20 16:06:49 2022

@author: kryis
"""

import yaml
import os

MAIN_DIR = os.path.dirname(os.getcwd())
CONF = yaml.safe_load(open(MAIN_DIR + "/conf.yml", "r"))
STRINGS = yaml.safe_load(open(MAIN_DIR + "/strings.yml", "r"))