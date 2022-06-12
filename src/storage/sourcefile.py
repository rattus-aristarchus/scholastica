#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 28 22:51:12 2022

@author: kryis
"""

import os
import collections

import data
import storage.storage as storage
import storage.parse as parse


class SourceFile:
    def __init__(self, address):
        self.address = address
        self.sources = []
        self.entries = []
        

def synch(source_file, tag_nest):
    clean(source_file)
    read(source_file, tag_nest)

def clean(source_file):
    for source in source_file.sources:
        source.clear_refs()
    source_file.sources.clear()
    for entry in source_file.entries:
        entry.clear_refs()
    source_file.entries.clear()
        
    
def read(source_file, tag_nest):
    #result = None
    
    with open(source_file.address, "r") as file:
        #By convention, the first lines in a file can be sources. Check, and 
        #if they are, read them.
        has_sources = False
        first_chunk = []
        
        for line in file:
            if line.isspace():
                break
            else:
                first_chunk.append(line)
            if parse.is_source(line):
                has_sources = True
        
        if has_sources:
            source_file.sources = parse.read_sources(first_chunk, tag_nest.tags)

        chunk = []
        chunks = 0
        for line in file:
            if line.isspace():
                chunks += 1
                #If the first chunk is a bunch of sources they shouldn't be
                #read as an entry
                if chunks == 1 and has_sources:
                    continue
                else:
                    entry = parse.read_entry(chunk, 
                                        tag_nest.tags, 
                                        source_file.sources)
                    if entry != None:
                     #   print("ENTRY CREATED: " + entry.text)
                        source_file.entries.append(entry)
                chunk = []
            else:
                chunk.append(line)
        

def edit_tag(old_name, new_name, source_file):
    storage.back_up(source_file.address)
    
    with open(source_file.address, "r") as file:
        new_file = ""
        for line in file:
            if parse.is_enclosed(line) and old_name in line:
                print(f"replacing {old_name} in line {line} with {new_name}")
                line = line.replace(old_name, new_name)
            new_file += line
        storage.write_safe(source_file.address, new_file)


def _chunk_has_tag(tag, chunk):
    if len(chunk > 0) and tag in chunk[-1]:
        return True;
    if len(chunk > 1) and tag in chunk[-2]:
        return True;
    return False