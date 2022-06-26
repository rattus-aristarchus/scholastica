#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun  4 19:36:01 2022

@author: kryis
"""

import kivy
kivy.require('2.1.0') # replace with your current kivy version !
from kivy.app import App
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import mainthread

from gui.tag_tree import TagNode
from gui.keyboard_listener import KeyboardListener
import storage.tagfile as tagfile
import storage.sourcefile as sourcefile
import rpc
import data
import util

STRINGS = util.STRINGS
CONF = util.CONF
LANG = CONF["misc"]["language"]
LOG = CONF["misc"]["log_filter"]

class Main(App):

    def __init__(self, tag_file):
        super().__init__()
        self.tag_file = tag_file
        self.title = "Scholastica"        
        
    def listen(self):
        msgr = rpc.Messenger(self.file_saved, 
                             self.query_tags,
                             self.query_sources)
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

    def query_tags(self):
        result = []
        for tag in self.tag_file.tag_nest.tags:
            result.append(tag.text)
        return result
    
    def query_sources(self, path):
        print(f"QUERY SOURCES: for path {path}")
        result = []
        for source_file in self.tag_file.source_files:
            if source_file.address == path:
                for source in source_file.sources:
                    result.append(source.text)
                break
        return result

    #Activated when the plugin has registered that a file has been saved
    def file_saved(self, path):
        print("FILE SAVED")
        try:
            #First, we check if the file is one of those already tracked by the 
            #application. If it is, all its content is reloaded.
            existing_file = None
            for check in self.tag_file.source_files:
                print("checking " + check.address)
                if check.address == path:
                    existing_file = check
                    break
                    
            if not existing_file == None:
                #If it is already tracked:   
                self.remove_file(existing_file)
                new_file = sourcefile.read(path, self.tag_file.tag_nest)
                if len(new_file.tags) > 0:
                    self.add_file(new_file)
            else:
                #If it isn't, we read the file and see if it has any tags at all. 
                #If it doesn't, there is no point in adding it
                new_file = sourcefile.read(path, self.tag_file.tag_nest)
                if len(new_file.tags) > 0:
                    self.add_file(new_file)
            return ""
        except Exception as err:
            print(f"Unexpected {err=}, {type(err)=}")

    @mainthread
    def remove_file(self, file):    
        self.view.ids['tree'].remove(file)
        sourcefile.clean(file)
        self.tag_file.source_files.remove(file)
        tagfile.write_tag_file(self.tag_file)
        
    @mainthread
    def add_file(self, file):
        self.view.ids['tree'].add(file)
        self.tag_file.source_files.append(file)
        tagfile.write_tag_file(self.tag_file)

class View(BoxLayout):
    pass   

class BasePopup(Popup):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.callback = None
    
    def enter(self):
        self.ok()        
    
    def escape(self):
        self.dismiss()
        
    def ok(self):
        if not self.callback == None:
            self.callback()
        self.dismiss()
        

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
        if not old_name == "":
            self.popup(message=STRINGS["popup"][2][LANG],
                       callback=lambda: self._edit_tag_in_files(old_name, 
                                                                new_name))
    
    """
    Removes the node from its current place in the tree. If that was the last
    place this tag was present in the tree, it is deleted as well.
    """
    def delete_node(self, tag_node):
        if  LOG < 1:
            print(f"CONTROLLER: deleting node {tag_node.entity.text}")
        
        if len(tag_node.entity.parents) > 1:
            tree = self.view.ids['tree']
            if tag_node.parent_node == tree.root:
                print("DELETE NODE: tag of root tree node has multiple parents")
            data.remove_child_tag(tag_node.entity, tag_node.parent_node.entity)
            self.save_file()
            
            tree.remove_node(tag_node)
        else:
            self._delete_tag_and_node(tag_node)
        
    def _delete_tag_and_node(self, tag_node):
        tag_nest = self.tag_file.tag_nest
        #If a  child tag has multiple parents, it will still be present on the
        #tree. If it has only one, then after deletion of the parent the child
        #is made a new root  
        
        #First, apply the changes to the data structure
        #Find the nodes whose tags have only one parent
        new_roots = []
        for child in tag_node.nodes:
            if isinstance(child, TagNode) and len(child.entity.parents) < 2:
                new_roots.append(child)
        
        #Tags from those nodes should be added as new roots
        for new_root in new_roots:
            tag_nest.roots.append(new_root.entity)
        #Remove all references to the deleted tag
        tag_node.entity.clear_refs()
        if tag_node.entity in tag_nest.roots:
            tag_nest.roots.remove(tag_node.entity)
        self.save_file()
        
        #Then, change the representation
        tree = self.view.ids['tree']
        for new_root in new_roots:
            tree.move_node(new_root, tree.root)
        
        tree.step_down()
        tree.remove_node(tag_node)
        """
        #Since the node can be present in multiple places in the tree if the
        #tag has multiple parents, we have to traverse the whole tree
        for node in tree.iterate_all_nodes():
            if isinstance(node, TagNode) and node.entity == tag_node.entity:
                tree.remove_node(node)
                """

    def scroll_to(self, widget):
        if self.view.ids['tree'].size[1] > self.view.ids['scroll'].size[1]:
            self.view.ids['scroll'].scroll_to(widget)
            
    def return_kbd(self):
        self.kbd_listener.bind_keyboard()
        
    def popup(self, message, callback=None):
        if LOG < 1:
            print(f"CONTROLLER: popup created with message {message}")
        
        popup = BasePopup()
        popup.ids["label"].text = message
        popup.callback = callback
        popup.open()
        
    def _edit_tag_in_files(self, old_name, new_name):
        if LOG < 1:
            print(f"CONTROLLER: _edit_tag_in_files, changing {old_name} to {new_name}")
        
        for source_file in self.tag_file.source_files:
            sourcefile.edit_tag(old_name, new_name, source_file)