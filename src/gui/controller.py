#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 27 15:56:59 2022

@author: kryis
"""

import logging
from gui.widgets import BasePopup
from gui.tag_tree import TagNode

import storage.tagfile as tagfile
import storage.sourcefile as sourcefile
from data.tag_nest import TagNest
from util import CONF
from util import STRINGS

logger = logging.getLogger(__name__)
LANG = CONF["misc"]["language"]

class Controller:
    
    def __init__(self, tag_file, view, return_kbd):
        self.tag_file = tag_file
        self.view = view
        self.tag_nest = tag_file.tag_nest
        self.tree = view.ids["tree"]
        self.return_kbd = return_kbd
 
        #the copied tagnode; this is needed for the copy-paste functionality
        self.clipboard = None
        self.cut = False
    
    def scroll_to(self, widget):
        if self.tree.size[1] > self.view.ids['scroll'].size[1]:
            self.view.ids['scroll'].scroll_to(widget)
    
    def save_file(self):
        tagfile.write_tag_file(self.tag_file)

    def popup(self, message, callback=None):
        logger.info(f"CONTROLLER: popup created with message {message}")
        
        popup = BasePopup()
        popup.ids["label"].text = message
        popup.callback = callback
        popup.open()
            
    def return_kbd(self):
        self.return_kbd() 
    
    def edit_tag(self, tag, new_name):
        old_name = tag.text
        tag.text = new_name
        self.save_file()
    
        if not old_name == "":
            self.popup(message=STRINGS["popup"][2][LANG],
                       callback=lambda: self._edit_tag_in_files(old_name, 
                                                                new_name))   
            
    def _edit_tag_in_files(self, old_name, new_name):
        logger.info(f"CONTROLLER: _edit_tag_in_files, changing {old_name} " \
                     + f"to {new_name}")
        
        for source_file in self.tag_file.source_files:
            sourcefile.edit_tag(old_name, new_name, source_file)
        
    def create_tag_at_selection(self):
        selected_node = self.tree.selected_node
        if (
                isinstance(selected_node, TagNode)
                and selected_node.editing
            ):
            return
        
        #Change data
        if selected_node == None:
            parent = None
            index = -1
        else:
            parent = selected_node.parent_node.entity
            #If the selected node is not a tagnode, the new node should be 
            #appended at the end of tagnodes
            if isinstance(selected_node, TagNode):
                index = parent.children.index(selected_node.entity) + 1
            else:
                index = len(parent.children)
        
        new_tag = self.tag_nest.create_tag(parent, index)
        self.save_file()
        
        #Change the representation
        if selected_node == None or selected_node.parent_node == self.tree.root:
            parent_node = None
        else:
            parent_node = selected_node.parent_node
        new_node = TagNode(new_tag, self)
        self.tree.insert_and_select(new_node, parent_node, index)
        
    """
    Copy the currently selected node to clipboard
    """
    def copy(self):
        if isinstance(self.tree.selected_node, TagNode):
            if not self.clipboard == None:
                self.tree.node_from_clipboard(self.clipboard)
                
            self.clipboard = self.tree.selected_node
            self.tree.clipboard_color(self.tree.selected_node)
            self.cut = False
    
    """
    Copy the currently selected node to clipboard with the flag "cut"
    """
    def cut(self):        
        if isinstance(self.tree.selected_node, TagNode):
            if not self.clipboard == None:
                self.tree.node_from_clipboard(self.clipboard)
               
            self.clipboard = self.tree.selected_node
            self.tree.clipboard_color(self.tree.selected_node)
            self.cut = True
        
    #TODO: the ability to change tag order
    #TODO: what happens if you paste a node onto itself
    """
    Insert node from clipboard as a child to the currently selected node
    """
    def paste(self):
        selected_node = self.tree.selected_node
        if (
                not selected_node == None 
                and not isinstance(selected_node, TagNode)
            ):
            self.popup(STRINGS["popup"][0][LANG])
            return
        if self.clipboard == None:
            return
        
        #If the node is cut and no tag is selected, the node becomes a new root
        if self.cut:
            #First, changes to the data structure
            destination = None if selected_node == None else selected_node.entity 
            self.tag_nest.move_tag(tag=self.clipboard.entity, 
                                   destination=destination)
            self.save_file()
            
            #Then, changes to the representation
            self.tree.move_node(node=self.clipboard, 
                                destination=selected_node)
            self.tree.normal_color(self.clipboard)
            self.clipboard = None
            
        #If the node is copied and no tag is selected, nothing happens
        elif not self.cut and not selected_node == None:
            #First, change the data structure   
            self.tag_nest.add_child_tag(child=self.clipboard.entity, 
                                        parent=self.tree.selected_node.entity)
            self.save_file()
        
            #Then, the representation
            self.tree.copy_node(node=self.clipboard, 
                                destination=selected_node)
            self.tree.normal_color(self.clipboard)
            self.clipboard = None
        
    """
    Lower the level of the currently selected node (make it the child of one of
    its siblings)
    """
    def lower_selected_node(self):
        node = self.tree.selected_node
        if (
                node == None 
                or node == self.tree.root
                or not isinstance(node, TagNode)
            ):
            return
        parent = node.parent_node 
        index = parent.nodes.index(node)
        if index == 0:
            #TODO: an error message to the user
            return
        prev_node = parent.nodes[index-1]
        
        #Change the data
        self.tag_nest.move_tag(tag=node.entity, 
                               destination=prev_node.entity)
        self.save_file()
        
        #Change the representation
        self.tree.move_node(node, prev_node)
    
    """
    Increase the level of the currently selected node (make it the sibling of
    its parent)
    """
    def raise_selected_node(self):
        node = self.tree.selected_node
        if (
                node == None
                or node == self.tree.root
                or node.parent_node == self.tree.root
                or not isinstance(node, TagNode)
            ):
            return
        parent = node.parent_node
        grandparent = parent.parent_node 
        index = grandparent.nodes.index(parent) + 1
        if grandparent == self.tree.root:
            destination = None
          #  index = -1
        else:
            destination = grandparent.entity
        
        #Change the data
        self.tag_nest.move_tag(node.entity, destination, index)
        self.save_file()
        
        #Change the representation
        self.tree.move_node(node, grandparent, index)
        
    """
    Removes the node from its current place in the tree. If that was the last
    place this tag was present in the tree, it is deleted as well.
    """
    def delete_node(self, tag_node):
        logger.info(f"CONTROLLER: deleting node {tag_node.entity.text}")
        
        if len(tag_node.entity.parents) > 1:
            #If the tag still has other parents, we're just removing the link
            #to the current parent
            if tag_node.parent_node == self.tree.root:
                logger.warning("DELETE NODE: tag of root tree node has multiple parents")
            self.tag_nest.remove_child_tag(child=tag_node.entity, 
                                           parent=tag_node.parent_node.entity)
            self.save_file()
            
            self.tree.remove_node(tag_node)
        else:
            #If the tag has only one parent, we're deleting the tag
            #First, apply the changes to the data structure
            new_roots = self.tag_nest.delete_tag(tag_node.entity)        
            self.save_file()
            
            #Then, change the representation
            for new_root in new_roots:
                self.tree.add_node(TagNode(new_root, self))
            self.tree.step_down()
            self.tree.remove_node(tag_node)
        