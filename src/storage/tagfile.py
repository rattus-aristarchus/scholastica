#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 28 22:51:01 2022

@author: kryis
"""

import os
import collections

import data
import storage.storage as storage
import storage.sourcefile as sourcefile

EMPTY_LINE = "\n"

class TagFile:
    def __init__(self, address):
        self.address = address
        self.tag_nest = data.TagNest()
        self.source_files = []
        

"""
Read a tag file and create a linked structure of tags with sources and entries
hanging off of them.
"""
def read_tag_file(address):
    result = TagFile(address)
    
    with open(address, "r") as file:

        indent = 0
        tag_stack = collections.OrderedDict()
        parent = None

        #The tagfile contains first a tree of tags, and then a list of source
        #files which use the tags
        tags = []
        source_paths = []
        after_break = False
        for line in file:
            if line.isspace():
                after_break = True
            elif not after_break:
                tags.append(line)
            else:
                source_paths.append(line)
        
        #First, build the tag structure
        for line in tags:
            #Based on the indent, figure out which tag the next line belongs to
            indent = _get_indent(line)
            _cut_stack(indent, tag_stack)            
            if len(tag_stack) > 0:
                parent = list(tag_stack.values())[-1]
            else:
                parent = None

            #Now, the string herself
            #The last symbol of the string is always a newline symbol
            string = line[indent:-1]
                        
            #The string can either be a tag that already exists, or a new 
            #one.
            tag = result.tag_nest.get(string)
            if tag == None:
                tag = data.Tag(string)
                result.tag_nest.tags.append(tag)                    
            if not parent is None:
                data.add_child_tag(tag, parent)
            if indent == 0:
                result.tag_nest.roots.append(tag)
            tag_stack[indent] = tag
        
        #Now, with a full structure of tags, all the sourcefiles can be read
        for line in source_paths:
            if len(line) == 0 or line.isspace():
                continue
            file = sourcefile.read(line[:-1], result.tag_nest)
            result.source_files.append(file)            
            
    return result

"""
Write a linked structure of tags with their contents as a file.
"""
def write_tag_file(tag_file):
    output = ""
    indent = 0
    written_tags = []
    
    storage.back_up(tag_file.address)

    #Traverse the roots; for each of them call a recursive function to get 
    #their string representation
    for root in tag_file.tag_nest.roots:
        output += _tag_to_string_deep(root, 
                                      indent, 
                                      written_tags, 
                                      tag_file)

    #Add the sources
    output += EMPTY_LINE
    for source_file in tag_file.source_files:
        output += source_file.address + "\n"
    
    #Write the result
    storage.write_safe(tag_file.address, output)


"""
Determine the number of whitespaces at the beginning of the line
"""
def _get_indent(line):
    spaces = 0
    for c in line:
        if c.isspace():
            spaces += 1
        else:
            break
    return spaces


def _cut_stack(cur_indent, stack):
    for indent in list(stack):
        if indent >= cur_indent:
            stack.pop(indent)

"""
Returns the string representation of a tag, its content and its children
"""
def _tag_to_string_deep(tag, indent, written_tags, tag_file):
    #First, the tag itself
    result = _tag_to_string(tag, indent)
    
    #Then, its content and children, recursively - unless they've already been 
    #written down elsewhere in the file    
    if not tag in written_tags:
        written_tags.append(tag)
#        for address in tag_file.content_by_tag[tag]:
#            for i in range(indent + 4):
#                result += " "
#            result += address + "\n"            
        for child in tag.children:
            result += _tag_to_string_deep(child, 
                                          indent + 4, 
                                          written_tags, 
                                          tag_file)
    return result


"""
Returns the string representation of a tag
"""
def _tag_to_string(tag, indent):
    result = ""
    for i in range(indent):
        result += " "
    result += tag.text
    result += "\n"
    return result