#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 27 14:31:45 2022

@author: kryis

Operations for handling files
"""

import os
from kivy.logger import Logger


TMP = ".tmp"
BAK = ".bak"


def make_backup_folder_for(path):
    Logger.info("Storage: creating backup folder for " + path)
    file_dir = os.path.dirname(path)
    backup_dir = os.path.join(file_dir, ".backup")
    if not (os.path.exists(backup_dir)):
        os.makedirs(backup_dir)
    return backup_dir


def back_up(path, backup_dir):    
    file_name = os.path.basename(path)
    backup_path = os.path.join(backup_dir, file_name)
    
    with open(path, "r") as file_obj:
        content = file_obj.read()
        with open(backup_path, "w") as backup:
            backup.write(content)


def write_safe(path, content):
    new_file = open(path + TMP, "w")
    new_file.write(content)
    new_file.close()

    existing = os.path.exists(path)
    if existing:
        #if os.path.exists(path + BAK):
        #    os.remove(path + BAK)
        os.rename(path, path + BAK)
    os.rename(new_file.name, path)
    if existing:
        os.remove(path + BAK)
