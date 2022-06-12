#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 27 14:31:45 2022

@author: kryis

Operations for handling files
"""

import os
import collections

import data

TMP = ".tmp"
BAK = ".bak"

def back_up(address):
    file_dir = os.path.dirname(address)
    file_name = os.path.basename(address)
    backup_dir = os.path.join(file_dir, "backup")
    if not (os.path.exists(backup_dir)):
        os.makedirs(backup_dir)
    backup_address = os.path.join(backup_dir, file_name)
    
    with open(address, "r") as file_obj:
        content = file_obj.read()
        with open(backup_address, "w") as backup:
            backup.write(content)
            
def write_safe(address, content):
    new_file = open(address + TMP, "w")
    new_file.write(content)
    existing = os.path.exists(address)
    if existing: 
        os.rename(address, address + BAK)
    os.rename(new_file.name, address)
    if existing:
        os.remove(address + BAK)