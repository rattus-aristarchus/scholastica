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


"""
The visual representation of a TagNest. Synchronization with the tagnest should
happen elsewhere, this just provides the basic methods for manipulating the 
tree.
"""
class TagTree(TreeView):
    
    def __init__(self, **kwargs):
        super().__init__(root_options=dict(text='Гнездо'), **kwargs)
        self.bind(minimum_height = self.setter("height"))        
        self.controller = None
        #the copied tagnode; this is needed for the copy-paste functionality
        self._copied = None
        self._cut = None
        
    
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
        #The enter key can finish the editing of an existing node if it's in
        #progress...
        if isinstance(self.selected_node, TagNode): 
            if self.selected_node.editing:
                self.selected_node.save_text()
                self.selected_node.label_mode()
                self.selected_node.load_text()
            else:
                #Or it can create a new tag
                new_tag = data.Tag()
                data.add_child_tag(self.selected_node.entity, new_tag)
                
                new_node = TagNode(new_tag, self.controller)
                self.add_node(new_node, self.selected_node)
                self.selected_node.is_open = True
                self.select_node(new_node)
                self.edit(False)
                        

    def edit(self, from_end):
        if (
                isinstance(self.selected_node, TagNode)\
                and not self.selected_node.editing
            ):
            self.selected_node.input_mode()
            self.selected_node.edit_text()
            if from_end:
                self.selected_node.cursor_to_end()
        
    
    def copy(self):
        if isinstance(self.selected_node, TagNode):
            self._copied = self.selected_node
            self._cut = None
    
    def cut(self):        
        if isinstance(self.selected_node, TagNode):
            self._copied = None
            self._cut = self.selected_node
    
    #TODO this function might not belong in this class; might be a good idea 
    #to move data manipulation to the controller and call it directly from the
    #kbd listener
    def paste(self):
        if not isinstance(self.selected_node, TagNode):
            return
        
        if not self._copied == None:
            #First, change the data structure
            data.add_child_tag(tag=self.selected_node.entity, 
                               child=self._copied.entity)
            self.controller.save_file()
        
            #Then, the representation
            self.copy_node(self._copied, self.selected_node)
            self._copied = None    
        elif not self._cut == None:
            old_parent = self._cut.parent_node
            new_parent = self.selected_node
            
            #First, change the data structure
            data.add_child_tag(tag=new_parent.entity, 
                               child=self._cut.entity)
            data.remove_child_tag(tag=old_parent.entity, 
                                  child=self._cut.entity)
            self.controller.save_file()
        
            #Then, the representation
            self.move_node(self._cut, self.selected_node)
            self._cut = None
    
    
    def move_node(self, node, destination):
        self.remove_node(node)
        self.add_node(node, destination)
        
    def copy_node(self, node, destination):
        new_node = node.copy()
        self.add_node(new_node, destination)
        for child in node.nodes:
            self.copy_node(child, new_node)
        
    def _select_and_scroll(self, node):
        self.select_node(node)
        self.controller.scroll_to(node)


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
        tag_node = TagNode(tag, self.controller)
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

    def copy(self):
        return EntNode(self.entity)

class SourceNode(EntNode):
    pass

    
class EntryNode(EntNode):
    pass    


class TagNode(EntNode):

    def __init__(self, tag, controller, **kwargs):
        super().__init__(tag, **kwargs)
        self.controller = controller
        self.input = self.ids['input']
        self.label = self.ids['label']
        self.remove_widget(self.input)
        self.editing = False
        
    def copy(self):
        return TagNode(self.entity, self.controller)
        
    """
    The following two methods change the appearance of the node
    """
    def edit_done(self):
        self.save_text()
        self.label_mode()
        self.load_text()
        
    def label_mode(self):
        if self.editing:
            self.remove_widget(self.input)
            self.input.focus = False
            self.add_widget(self.label)
            self.editing = False
            self.controller.return_kbd()
    
    def input_mode(self):
        if not self.editing:
            self.remove_widget(self.label)
            self.add_widget(self.input)
            self.input.focus = True
            self.editing = True
    
    def cursor_to_end(self):
        self.input.cursor = (len(self.input.text), 0)
        
    """
    These change the data based on user input
    """
    def save_text(self):
        if self.ids['input'].text == "":
            self.controller.delete_tag_and_node(self)
        else:
            self.controller.edit_tag(self.entity, self.ids['input'].text)        
                
    def edit_text(self):
        self.ids['input'].text = self.entity.text
        