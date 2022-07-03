#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 28 22:51:12 2022

@author: kryis
"""

from kivy.logger import Logger

import storage.storage as storage
import storage.parse as parse
from util import CONF
from util import STRINGS

#logger = logging.getLogger(__name__)
LANG = CONF["misc"]["language"]

class SourceFile:
    def __init__(self, address):
        self.address = address
        self.sources = []
        self.entries = []
        #Tags that are encountered in the sourcefile
        self.tags = []
        
  #  def __eq__(self, o):
  #      return isinstance(o, SourceFile) and self.address == o.address
  #      
  #  def __hash__(self):
  #      return hash(self.address)

#def synch(source_file, tag_nest):
 #   clean(source_file)
 #   read(source_file, tag_nest)


#Read the file at the address and create a sourcefile object, while also 
#connecting entries and sources to specified tags if the tags are present in 
#the tag nest
def read(address, tag_nest):
    result = SourceFile(address)
    messages = []
    
    try:
        with open(address, "r") as file:        
            #The lines before the first empty line in a file can be sources. Split
            #the file in two halves, before the first empty line and after; if 
            #the first lines are sources, read them separately; if not, add them
            #to the rest to be read as entries
            
            has_sources = False
            first_chunk = []
            entries = []
            after_break = False
            
            for line in file:
                if line.isspace():
                    after_break = True
                    entries.append(line)
                elif after_break:
                    entries.append(line)
                else:
                    first_chunk.append(line)
                    if parse.is_source(line):
                        has_sources = True
            #Since reading a chunk is triggered by an empty line, the last line 
            #always needs to be empty
            entries.append(parse.EMPTY_LINE)
            
            if has_sources:
                result.sources = parse.read_sources(first_chunk, tag_nest)
                for source in result.sources:
                    Logger.debug(f"Sourcefile: created source {source.text[:100]}")
                    result.tags += source.tags
            else:
                entries = first_chunk + [parse.EMPTY_LINE] + entries
    
    
            #Read the lines as entries
            chunk = []
            for line in entries:
                if line.isspace():
                    entry = parse.read_entry(chunk, 
                                             tag_nest, 
                                             result.sources)
                    if entry != None:
                     #   Logger.debug(f"Sourcefile: created entry {entry.text[:100]}")
                        result.entries.append(entry)
                        result.tags += entry.tags
                    chunk = []
                else:
                    chunk.append(line)   
    except FileNotFoundError as e:
        Logger.error(e.strerror + ": " + e.filename)
        message = STRINGS["error"][0][LANG][0] + \
                  e.filename + \
                  STRINGS["error"][0][LANG][1]
        messages.append(message)
        result = None
        
    return result, messages

def edit_tag(old_name, new_name, source_file):
    storage.back_up(source_file.address)
    
    with open(source_file.address, "r") as file:
        new_file = ""
        for line in file:
            if parse.is_enclosed(line) and old_name in line:
            #    Logger.info(f"replacing {old_name} in line {line} with " \
            #                 + f" {new_name}")                
                line = line.replace(old_name, new_name)
            new_file += line
        storage.write_safe(source_file.address, new_file)


def _chunk_has_tag(tag, chunk):
    if len(chunk > 0) and tag in chunk[-1]:
        return True;
    if len(chunk > 1) and tag in chunk[-2]:
        return True;
    return False