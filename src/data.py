#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
The basic data structures.

Created on Fri May 27 14:30:56 2022

@author: kryis
"""

class Tag:
    """
    Tags are used to organize entries and sources. Tags form a directed graph.
    Every tag can have parent tags and child tags. The "content" variable lists
    all the Entries and Sources attached to the tag.
    
    Which makes me think. Ideally, data should only be stored once, in one 
    place. Maybe the "tags" variables from Entry and Source should be deleted?
    """
    def __init__(self, text=""):
        self.text = text
        self.parents = []
        self.children = []
        #The sources and entries which have the tag
        self.content = []
    
    def clear_refs(self):
        for content in self.content:
            content.tags.remove(self)
        for tag in self.parents:
            tag.children.remove(self)
        for tag in self.children:
            tag.parents.remove(self)
        
    #I am defining the eq and hash methods so that the "in" keyword will be 
    #able to tell if the tag is present in a list of tags    
    def __eq__(self, o):
        return isinstance(o, Tag) and self.text == o.text
        
    def __hash__(self):
        return hash(self.text)
        
    
class Entry:
    def __init__(self, text):
        self.text = text
        self.tags = []
        self.source = None
        self.page = 0
        
    def clear_refs(self):
        for tag in self.tags:
            if self in tag.content:
                tag.content.remove(self)
        

class Source:
    def __init__(self, text):
        self.text = text
        self.tags = []  
    
        #TODO: for some reason i don't like this method. make it a standalone 
        #function maybe?
    def clear_refs(self):
        for tag in self.tags:
            if self in tag.content:
                tag.content.remove(self)
         
    def __eq__(self, o):
        return isinstance(o, Source) and self.text == o
    
    def __hash__(self):
        return hash(self.text)
        

class TagNest:
    
    def __init__(self):
        self.tags = []
        self.roots = []
    

    def get(self, name):
        for tag in self.tags:
            if tag.text == name:
                return tag
        return None    


def add_tag_to_source(tag, source):
    if not tag in source.tags:
        source.tags.append(tag)
    if not source in tag.content:
        tag.content.append(source)

def add_tag_to_entry(tag, entry):
    if not tag in entry.tags:
        entry.tags.append(tag)
    if not entry in tag.content:
        tag.content.append(entry)

#TODO: this is not used anywhere, that can't be right
def remove_tag_from_content(tag, content):
    if tag in content.tags:
        content.tags.remove(tag)
    if content in tag.content:
        tag.content.remove(content)

def add_child_tag(child, tag, index=-1):
    if not child in tag.children:
        if index == -1:
            tag.children.append(child)
        else:
            tag.children.insert(index, child)
    if not tag in child.parents:
        child.parents.append(tag)
        
def remove_child_tag(child, tag):
    if tag in child.parents:
        child.parents.remove(tag)
    if child in tag.children:
        tag.children.remove(child)
    