#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun 26 17:40:56 2022

@author: kryis

All the basic operations with data
"""

from data.base_types import Tag, Source, Entry

class TagNest:
    
    def __init__(self):
        self.tags = []
        self.roots = []
    

    def get(self, name):
        for tag in self.tags:
            if tag.text == name:
                return tag
        return None

    def add_tag_to_source(self, tag, source):
        if not tag in source.tags:
            source.tags.append(tag)
        if not source in tag.content:
            tag.content.append(source)
    
    def add_tag_to_entry(self, tag, entry):
        if not tag in entry.tags:
            entry.tags.append(tag)
        if not entry in tag.content:
            tag.content.append(entry)
    
    #TODO: this is not used anywhere, that can't be right
    def remove_tag_from_content(self, tag, content):
        if tag in content.tags:
            content.tags.remove(tag)
        if content in tag.content:
            tag.content.remove(content)
    
    def add_child_tag(self, child, parent=None, index=-1):
        if parent == None:
            if index == -1:
                self.roots.append(child)
            else:
                self.roots.insert(index, child)
        else:
            if child in self.roots:
                self.roots.remove(child)
                
            if not child in parent.children:
                if index == -1:
                    parent.children.append(child)
                else:
                    parent.children.insert(index, child)
            if not parent in child.parents:
                child.parents.append(parent)
            
    def remove_child_tag(self, child, parent):
        if parent in child.parents:
            child.parents.remove(parent)
        if child in parent.children:
            parent.children.remove(child)
    
    def create_tag(self, parent, index=-1):
        new_tag = Tag()            
        self.tags.append(new_tag)
        
        #If no node is selected, the new node becomes a root
        if parent == None:
            self.roots.append(new_tag)
        else:
            self.add_child_tag(new_tag, parent, index)  
            
        return new_tag
    
    def move_tag(self, tag, destination, index=-1):
        if tag in self.roots:
            self.roots.remove(tag)
        else:
            for parent in tag.parents:
                self.remove_child_tag(tag, parent)
            
        self.add_child_tag(tag, destination, index)
            
    """
    Returns a list of tags that have become new roots
    """
    def delete_tag(self, tag):
        #Find the nodes whose tags have only one parent. Those are added to 
        #the nest as new roots
        new_roots = []
        for child in tag.children:
            if len(child.parents) < 2:
                new_roots.append(child)
        self.roots += new_roots
        
        #Remove all references to the deleted tag
        tag.clear_refs()
        if tag in self.roots:
            self.roots.remove(tag)

        return new_roots