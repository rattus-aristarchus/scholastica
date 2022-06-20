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
from util import CONF


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
        self._clipboard = None
        self._cut = False
        
    
    def show(self, tag_nest):
        self.tag_nest = tag_nest
        for root_tag in tag_nest.roots:
        #    tag_node = TagNode()
        #    tag_node.add_widget(Label(text="sup"))
        #    self.add_node(tag_node)
            self._show_deep(root_tag, None, [])

    def remove(self, source_file):
        entities = source_file.sources + source_file.entries
        for entity in entities:
            for node in self.iterate_all_nodes():
                if (
                        isinstance(node, EntNode) 
                        and node.entity.text == entity.text
                    ):
                    self.remove_node(node)

    def add(self, source_file):
        for source in source_file.sources:
            for tag in source.tags:
                parent = self._find_node(tag)
                if not parent == None:
                    source_node = SourceNode(source)
                    self.add_node(source_node, parent)
                else:
                    print("source has a tag that is not present on the tag tree")
        
        for entry in source_file.entries:
            for tag in entry.tags:
                parent = self._find_node(tag)
                if not parent == None:
                    entry_node = EntryNode(entry)
                    self.add_node(entry_node, parent)
                else:
                    print("entry  has a tag that is not present on the tag tree")

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
        if (
                isinstance(self.selected_node, TagNode)
                and self.selected_node.editing
            ):
            self.selected_node.save_text()
            self.selected_node.label_mode()
            self.selected_node.load_text()
        else:
            #Or it can create a new tag
            new_tag = data.Tag()
            
            #If no node is selected, the new node becomes a root
            if self.selected_node == None:
                parent_node = self.root
                parent = None
                self.tag_nest.roots.append(new_tag)
            else:
                parent_node = self.selected_node
                parent = self.selected_node.entity
                data.add_child_tag(parent, new_tag)
                            
            new_node = TagNode(new_tag, self.controller)
            self.add_node(new_node, parent)
            if not self.selected_node == None:
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
        
    #TODO: copy and cut should change the color of the relevant node
    
    def copy(self):
        if isinstance(self.selected_node, TagNode):
            if not self._clipboard == None:
                self._from_clipboard(self._clipboard)
                
            self._to_clipboard(self.selected_node)
            self._cut = False
    
    def cut(self):        
        if isinstance(self.selected_node, TagNode):
           if not self._clipboard == None:
               self._from_clipboard(self._clipboard)
               
           self._to_clipboard(self.selected_node)
           self._cut = True
    
    def _to_clipboard(self, node):
        self._clipboard = node
        
        node.even_color = CONF["colors"]["clipboard_background"]
        node.odd_color = CONF["colors"]["clipboard_background"]
    
    def _from_clipboard(self, node):
        self._clipboard = None
        
        if isinstance(node, TagNode):
            node.even_color = CONF["colors"]["tag_background"]
            node.odd_color = CONF["colors"]["tag_background"]
        
    
    #TODO this function might not belong in this class; might be a good idea 
    #to move data manipulation to the controller and call it directly from the
    #kbd listener
    #TODO: popups with messages to the user
    def paste(self):
        if (
                not self.selected_node == None 
                and not isinstance(self.selected_node, TagNode)
            ):
            return
        if self._clipboard == None:
            return
        
        #If the node is copied and no tag is selected, nothing happens; if the
        #node is cut and no tag is selected, the node becomes a new root
        if self._cut:
            cut_tag = self._clipboard.entity
            
            #First, changes to the data structure
            #Remove the tag from its parent node
            if self._clipboard.parent_node == self.root:
                if cut_tag in self.tag_nest.roots:
                    self.tag_nest.roots.remove(cut_tag)
                else:
                    print(f"PASTE TAG: the tree node of tag {cut_tag.text} " + \
                          "is a root but the tag itself isn't")
            else:
                data.remove_child_tag(tag=self._clipboard.parent_node.entity, 
                                      child=cut_tag)
            #Add the tag to the new node
            if self.selected_node == None:
                self.tag_nest.roots.append(cut_tag)
            else:
                data.add_child_tag(tag=self.selected_node.entity, 
                                   child=cut_tag)
                            
            self.controller.save_file()
            
            #Then, changes to the representation
            self.move_node(self._clipboard, self.selected_node)
            if not self.selected_node == None:
                self.selected_node.is_open = True
            self.select_node(self._clipboard)
            self._from_clipboard(self._clipboard)
        elif not self._clipboard and not self.selected_node == None:
            #First, change the data structure            
            tag = self.selected_node.entity
            child=self._clipboard.entity
            data.add_child_tag(tag, child)
            if child in self.tag_nest.roots:
                self.tag_nest.roots.remove(child)
            self.controller.save_file()
        
            #Then, the representation
            self.copy_node(self._clipboard, self.selected_node)
            if not self.selected_node == None:
                self.selected_node.is_open = True
            self.select_node(self._clipboard)
            self._from_clipboard(self._clipboard)
    
    def move_node(self, node, destination):
        self.remove_node(node)
        self._add_tag_node(node, destination)
        
    def copy_node(self, node, destination):
        new_node = node.copy()
        self.add_node(new_node, destination)
        for child in node.nodes:
            self.copy_node(child, new_node)
    
    """
    Inserts a tag node before all content nodes at the destination
    """
    def _add_tag_node(self, tag_node, destination):
        after_tag_node = []
        if destination == None:
            destination = self.root
        for node in destination.nodes:
            if not isinstance(node, TagNode):
                after_tag_node.append(node)
                
        for node in after_tag_node:
            self.remove_node(node)
            
        self.add_node(tag_node, destination)
        
        for node in after_tag_node:
            self.add_node(node, destination)
        
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
            
        #Repeat the function for all of its children
        if len(tag.children) > 0:
            parents.append(tag)
            for child in tag.children:
                self._show_deep(child, tag_node, parents)
            parents.remove(tag)
            
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

    def _find_node(self, tag):
 #       print(str(list(self.iterate_all_nodes())))
        for node in list(self.iterate_all_nodes()):
            if isinstance(node, TagNode) and node.entity.text == tag.text:
                return node
        return None

class EntNode(GridLayout, TreeViewNode):

    def __init__(self, entity, **kwargs):
        super().__init__(**kwargs)
        if entity == None:
            print("creating node with None entity")
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
        