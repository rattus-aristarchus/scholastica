#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun  4 19:36:01 2022

@author: kryis
"""

import kivy
kivy.require('2.1.0') # replace with your current kivy version !
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout

from gui.tag_tree import TagNode
from gui.keyboard_listener import KeyboardListener
import storage.tagfile as tagfile
import storage.sourcefile as sourcefile
import rpc

class Main(App):

    def __init__(self, tag_file):
        super().__init__()
        self.tag_file = tag_file
        self.title = "Scholastica"        
        
    def listen(self):
        msgr = rpc.Messenger(self.file_saved)
        msgr.start()

    def build(self):
        self.view = View()
        tree = self.view.ids['tree']
        self.kbd_listener = KeyboardListener(tree)
        tree.controller = NodeController(self.tag_file, 
                                         self.view, 
                                         self.kbd_listener)
        tree.show(self.tag_file.tag_nest)
        return self.view        


    #Activated when the plugin has registered that a file has been saved
    def file_saved(self, path):
        #First, we check if the file is one of those already tracked by the 
        #application. If it is, all its content is reloaded.
        existing = None
        for check in self.tag_file.source_files:
            print("checking " + check.address)
            if check.address == path:
                existing = check
                break
                
        if not existing == None:
            #If it is already tracked:
            sourcefile.clean()
            self.tag_file.source_files.remove(existing)
            source_file = sourcefile.read(path, self.tag_file.tag_nest)
            if len(source_file.tags) > 0:
                self.tag_file.source_files.append(source_file)
            #Write changes
            tagfile.write_tag_file(self.tag_file)
        else:
            #If it isn't, we read the file and see if it has any tags at all. 
            #If it doesn't, there is no point in adding it
            source_file = sourcefile.read(path, self.tag_file.tag_nest)
            if len(source_file.tags) > 0:
                self.tag_file.source_files.append(source_file)
            #Write changes
            tagfile.write_tag_file(self.tag_file)
        return ""
    

class View(BoxLayout):
    pass        


class NodeController:
    
    def __init__(self, tag_file, view, kbd_listener):
        self.tag_file = tag_file
        self.view = view
        self.kbd_listener = kbd_listener
    
    def save_file(self):
        tagfile.write_tag_file(self.tag_file)
    
    def edit_tag(self, tag, new_name):
        old_name = tag.text
        tag.text = new_name
        self.save_file()
        #TODO: this is probably not a good idea - the text files can be open
        #in a text editor while we're writing into them
        if not old_name == "":
            for source_file in self.tag_file.source_files:
                sourcefile.edit_tag(old_name, new_name, source_file)
    
    def delete_tag_and_node(self, tag_node):
        #If a  child tag has multiple parents, it will still be present on the
        #tree. If it has only one, then after deletion of the parent the child
        #is made a new root  
        
        #First, apply the differences to the data structure
        #Find the nodes whose tags have only one parent
        new_roots = []
        for child in tag_node.nodes:
            if isinstance(child, TagNode) and len(child.entity.parents) < 2:
                new_roots.append(child)
        
        #Tags from those nodes should be added as new roots
        for new_root in new_roots:
            self.tag_file.tag_nest.roots.append(new_root.entity)
        #Remove all references to the deleted tag
        tag_node.entity.clear_refs()
        self.save_file()
        
        #Then, change the representation
        tree = self.view.ids['tree']
        for new_root in new_roots:
            tree.move_node(new_root, tree.root)
        #Since the node can be present in multiple places in the tree if the
        #tag has multiple parents, we have to traverse the whole tree
        for node in tree.iterate_all_nodes():
            if isinstance(node, TagNode) and node.entity == tag_node.entity:
                tree.remove_node(node)
    
    def scroll_to(self, widget):
        if self.view.ids['tree'].size[1] > self.view.ids['scroll'].size[1]:
            self.view.ids['scroll'].scroll_to(widget)
            
    def return_kbd(self):
        self.kbd_listener.bind_keyboard()      