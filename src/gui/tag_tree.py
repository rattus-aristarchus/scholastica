#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun  5 16:19:01 2022

@author: kryis
"""

from kivy.uix.treeview import TreeView
from kivy.uix.treeview import TreeViewLabel
from kivy.uix.treeview import TreeViewNode

from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout

import data
from data import Source
from data import Entry


class TagTree(TreeView):
    
    def __init__(self, **kwargs):
        super().__init__(root_options=dict(text='Гнездо'), **kwargs)
        self.bind(minimum_height = self.setter("height"))
        #the copied tagnode; this is needed for the copy-paste functionality
        self.copied = None
        
    """
    This should be called when a textinput is finished editing to return 
    control to keyboard commands.
    """
    def kbd_callback(self, return_kbd):
        self.return_kbd = return_kbd
        
    def file_callback(self, save_file):
        self.save_file = save_file

    def edit_callback(self, edit_tag):
        self.edit_tag = edit_tag
    
    def scroll_callback(self, scroll_to):
        self.scroll_to = scroll_to
    
    
    def show(self, tag_nest):
        for root_tag in tag_nest.roots:
        #    tag_node = TagNode()
        #    tag_node.add_widget(Label(text="sup"))
        #    self.add_node(tag_node)
            self._show_deep(root_tag, None, [])


    def step_down(self):
        if self.selected_node == None:
            if len(self.root.nodes) > 0:
                self._select_and_scroll(self.root.nodes[0])
        elif self.selected_node.is_leaf or not self.selected_node.is_open:
            self._traverse_down(self.selected_node)
        else:
            self._select_and_scroll(self.selected_node.nodes[0])
    
    def step_down_over(self):        
        if self.selected_node == None:
            if len(self.root.nodes) > 0:
                self._select_and_scroll(self.root.nodes[0])
        else:
            self._traverse_down(self.selected_node)
        
    def step_up(self):
        self._step_up(False)
        
    def step_up_over(self):
        self._step_up(True)
        
    def _step_up(self, over):
        if self.selected_node == None or self.selected_node == self.root:
            if len(self.root.nodes) > 0:
                last_node = list(self.iterate_open_nodes())[-1]
                self._select_and_scroll(last_node)
            return
        
        parent = self.selected_node.parent_node
        
        index = parent.nodes.index(self.selected_node)
        if index == 0:
            if parent == self.root:
                self.deselect_node(self.selected_node)
            else:
                self._select_and_scroll(parent)
        else:
            if over:
                prev_node = parent.nodes[index - 1]
            else:
                prev_node = self._last_node(parent.nodes[index - 1])
            self._select_and_scroll(prev_node)        
    
        
    def step_out(self):
        if self.selected_node == None:
            return
        
        if self.selected_node.is_open:
            self.toggle_node(self.selected_node)
        else:
            parent = self.selected_node.parent_node
            if not parent == self.root or parent == None:
                self.toggle_node(parent)
                self._select_and_scroll(parent)

    def step_in(self):
        select = self.selected_node
        if (
                not select == None 
                and not select.is_leaf 
                and not select.is_open
            ):
            self.toggle_node(select)
            self.step_down()

    def enter(self):
        if self.selected_node.editing:
            self.selected_node.save_text()
            self.selected_node.label_mode()
            self.selected_node.load_text()
                        

    def edit(self, from_end):
        if (
                isinstance(self.selected_node, TagNode)\
                and not self.selected_node.editing
            ):
            self.selected_node.input_mode()
            self.selected_node.edit_text()
        
    
    def copy(self):
        if isinstance(self.selected_node, TagNode):
            self.copied = self.selected_node
            
    
    
    def paste(self):
        if isinstance(self.selected_node, TagNode):
            data.add_child_tag(tag=self.selected_node.entity, 
                               child=self.copied.entity)
            self.save_file()
            
    def _select_and_scroll(self, node):
        self.select_node(node)
        self.scroll_to(node)


    def _show_deep(self, tag, parent_node, parents):
        """
        Traverse the tag and all its children recursively and add them to the
        tree.
        """ 
        #To avoid cycles in our tree we stop the traversion if the tag is 
        #already present among its parents or grandparents of any level.
        if tag in parents:
            return
        
        #Display the tag itself
        tag_node = TagNode(tag, self.return_kbd, self.save_file, self.edit_tag)
        if parent_node == None:
            self.add_node(tag_node)
        else:
            self.add_node(tag_node, parent_node)
            
        #Display all sources with the tag
        for content in tag.content:
            if isinstance(content, Source):
                source_node = SourceNode(content)
                self.add_node(source_node, tag_node)
        
        #Display all entries
        for content in tag.content:
            if isinstance(content, Entry):
                entry_node = EntryNode(content)
                self.add_node(entry_node, tag_node)
        
        #Repeat the function for all of its children
        if len(tag.children) > 0:
            parents.append(tag)
            for child in tag.children:
                self._show_deep(child, tag_node, parents)
            parents.remove(tag)
        
    #TODO this should return the value, not do it herself
    def _traverse_down(self, cur_node):
        parent = cur_node.parent_node
        if parent == None:
            self.deselect_node(self.selected_node)
            return
        
        index = parent.nodes.index(cur_node)
        
        if index < len(parent.nodes) - 1:
            self._select_and_scroll(parent.nodes[index + 1])
        else:
            self._traverse_down(parent)

    def _last_node(self, node):
        if node.is_leaf or not node.is_open:
            return node
        else:
            last = node.nodes[-1]
            return self._last_node(last)
            
#    def on_touch_down(self, touch):
#        print("i've got an event!")

class EntNode(GridLayout, TreeViewNode):

    def __init__(self, entity, **kwargs):
        super().__init__(**kwargs)
        self.entity = entity
        self.load_text()
            
    def load_text(self):
        self.ids['label'].text = self.entity.text


class SourceNode(EntNode):
    pass

    
class EntryNode(EntNode):
    pass    


class TagNode(EntNode):

    def __init__(self, tag, return_kbd, save_file, edit_tag, **kwargs):
        super().__init__(tag, **kwargs)
        #The callback for returning control to the main keyboard
        self.return_kbd = return_kbd
        self.save_file = save_file
        self.edit_tag = edit_tag
        self.input = self.ids['input']
        self.label = self.ids['label']
        self.remove_widget(self.input)
        self.editing = False
        
    def edit_done(self):
        self.save_text()
        self.label_mode()
        self.load_text()
        
    """
    The following two methods change the appearance of the node
    """
    def label_mode(self):
        if self.editing:
            self.remove_widget(self.input)
            self.input.focus = False
            self.add_widget(self.label)
            self.editing = False
            self.return_kbd()
    
    def input_mode(self):
        if not self.editing:
            self.remove_widget(self.label)
            self.add_widget(self.input)
            self.input.focus = True
            self.editing = True
    
    """
    These change the data based on user input
    """
    def save_text(self):
        old_name = self.entity.text
        self.entity.text = self.ids['input'].text
        self.save_file()
        self.edit_tag(old_name, self.entity.text)        
        
    def edit_text(self):
        self.ids['input'].text = self.entity.text