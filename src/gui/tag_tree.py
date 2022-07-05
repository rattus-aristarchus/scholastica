#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun  5 16:19:01 2022

@author: kryis
"""

from kivy.logger import Logger
from kivy.uix.treeview import TreeView
from kivy.uix.treeview import TreeViewNode
from kivy.uix.gridlayout import GridLayout

from data.base_types import Source
from data.base_types import Entry
from util import CONF
from util import STRINGS

#logging.basicConfig(level=logging.DEBUG)
#logger = logging.getLogger(__name__)
LANG = CONF["misc"]["language"]

#TODO: it should be possible to clear the clipboard

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
        
    """
    Traverse all the roots in the nest recursively and add them to the
    tree.
    """ 
    def show(self, tag_file):
        Logger.info(f"TagTree: showing tag file {tag_file.address}")
        
        self.tag_file = tag_file
        self.tag_nest = tag_file.tag_nest
        for root_tag in tag_file.tag_nest.roots:
        #    tag_node = TagNode()
        #    tag_node.add_widget(Label(text="sup"))
        #    self.add_node(tag_node)
            self._show_deep(root_tag, None, [])

    #TODO: change functions such as _show_deep into internal functions of their
    #parent function. it's gonna be moe logical since they have no use outside 
    #their parent anyway
    
    def _show_deep(self, tag, parent_node, parents):
        #To avoid cycles in our tree we stop the traversion if the tag is 
        #already present among its parents or grandparents of any level.
        if (
                tag in parents 
                or (
                    not parent_node == None
                    and tag == parent_node.entity
                )
            ):
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
                source_node = SourceNode(content, 
                                         self.tag_file.content_by_source[content])
                self.add_node(source_node, tag_node)
        
        #Display all entries
        for content in tag.content:
            if isinstance(content, Entry):
                entry_node = EntryNode(content,
                                       self.tag_file.content_by_source[content])
                self.add_node(entry_node, tag_node)

    """
    Remove all nodes corresponding to entities contained in the source file.
    """
    def remove_all_from(self, source_file):
        Logger.info(f"TagTree: removing source file {source_file.address}")
        
        entities = source_file.sources + source_file.entries
        for entity in entities:
            Logger.debug(f"TagTree: removing entity {entity.text[:100]}")
            for node in self.iterate_all_nodes():
                if (
                        isinstance(node, EntNode) 
                        and node.entity.text == entity.text
                    ):
                    Logger.debug("TagTree: found matching node, removing")
                    self.remove_node(node)

    """
    Add new nodes for every entity in the source file
    """
    def add_all_from(self, source_file):
        Logger.info(f"TagTree: adding source file {source_file.address}")
        
        for source in source_file.sources:
            for tag in source.tags:
                parent = self._find_node(tag)
                if not parent == None:
                    source_node = SourceNode(source, source_file)
                    self.add_node(source_node, parent)
                else:
                    Logger.warning(f"source {source.text} has a tag {tag.text}"
                                    + f" that is not present on the tag tree")
        
        for entry in source_file.entries:
            for tag in entry.tags:
                parent = self._find_node(tag)
                if not parent == None:
                    entry_node = EntryNode(entry, source_file)
                    self.add_node(entry_node, parent)
                else:
                    Logger.warning(f"entry {entry.text} has a tag {tag.text}" \
                                    + f" that is not present on the tag tree")


    def _find_node(self, tag):
        for node in list(self.iterate_all_nodes()):
            if isinstance(node, TagNode) and node.entity.text == tag.text:
                return node
        return None

    #TODO: it might be a good idea to step over nodes that aren't tag nodes -
    #if we really don't want the user to interact with them.
    #Either that, or implement opening the relevant .txt file when trying to 
    #edit entries and sources
    """
    Select next node
    """
    def step_down(self):
        if self.selected_node == None:
            if len(self.root.nodes) > 0:
                self._select_and_scroll(self.root.nodes[0])
        elif self.selected_node.is_leaf or not self.selected_node.is_open:
            self._traverse_down(self.selected_node)
        else:
            self._select_and_scroll(self.selected_node.nodes[0])
    
    """
    Select next node, stepping over lower-level nodes
    """
    def step_down_over(self):        
        if self.selected_node == None:
            if len(self.root.nodes) > 0:
                self._select_and_scroll(self.root.nodes[0])
        else:
            self._traverse_down(self.selected_node)
    
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
    
    """
    Select previous node
    """
    def step_up(self):
        self._step_up(False)
        
    """
    Select previous node, stepping over lower-level nodes
    """
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
    
    def _last_node(self, node):
        if node.is_leaf or not node.is_open:
            return node
        else:
            last = node.nodes[-1]
            return self._last_node(last)
    
    def _select_and_scroll(self, node):
        self.select_node(node)
        self.controller.scroll_to(node)   
    
    """
    Select the parent of current node and collapse the current node
    """
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

    """
    Expand current node and select its first child
    """
    def step_in(self):
        select = self.selected_node
        if (
                not select == None 
                and not select.is_leaf 
                and not select.is_open
            ):
            self.toggle_node(select)
            self.step_down()

    """
    Add a new child node to the parent of currently selected node
    """
    def insert_and_select(self, node, parent, index):
        if parent == None:
            self.add_node(node)
        elif index == -1:
            self.add_tag_node(node, parent)
        else:
            self.insert_node(node, parent, index)
        
        if not parent == None:
            parent.is_open = True
        self.select_node(node)
    #    self.edit_node(False)
 
    
    
    def move_node(self, node, destination, index=-1):
        self.remove_node(node)
        if index == -1:
            self.add_tag_node(node, destination)
        else:
            self.insert_node(node, destination, index)
        
        if not destination == None:
            destination.is_open = True
        self.select_node(node)
        
    def copy_node(self, node, destination):
        if node.parent_node == self.root:
            self.remove_node(node)
            
        self._copy_node(node, destination)
            
        if not destination == None:
            destination.is_open = True
        self.select_node(node)
        
    def _copy_node(self, node, destination):
        new_node = node.copy()
        self.add_node(new_node, destination)
        for child in node.nodes:
            self.copy_node(child, new_node)
        
    
    def clipboard_color(self, node):
        node.even_color = CONF["colors"]["clipboard_background"]
        node.odd_color = CONF["colors"]["clipboard_background"]
    
    def normal_color(self, node):
        node.even_color = CONF["colors"]["tag_background"]
        node.odd_color = CONF["colors"]["tag_background"]
    
    """
    Inserts a tag node before all content nodes at the destination
    """
    def add_tag_node(self, tag_node, destination):
        after_tag_node = []
        if destination == None:
            destination = self.root
            
        index = len(destination.nodes)
        for node in destination.nodes:
            if not isinstance(node, TagNode):
                index = destination.nodes.index(node)
        self.insert_node(tag_node, destination, index)
        

    #TODO: check border cases for all functions and provide error messages    
    """
    Inserts a node among the children of the specified parent at the index
    """
    def insert_node(self, node, parent, index):
        if node == self.root:
            Logger.warning(f"INSERT NODE: trying to insert root node into "\
                            f"node {parent.entity.text} at index {index}")
            return
        if index > len(parent.nodes):
            Logger.warning(f"INSERT NODE: index too large, inserting node "\
                            f"{node.entity.text} into parent "\
                            f"{parent.entity.text} at index {index} while the"\
                            f"parent only has {len(parent.nodes)} children")
            return
        #Remove all nodes after node_after
        
        after_node = parent.nodes[index:]
        for next_node in after_node:
            self.remove_node(next_node)
                
        #Add the inserted node and then put back all the nodes removed before
        self.add_node(node, parent)
        for next_node in after_node:
            self.add_node(next_node, parent)
    
    #TODO: this does not remove all instances for some reason
    def remove_all_instances(self, node):
        if node == self.root:
            return
        Logger.info(f"TagTree: removing instances of node {node.entity.text}")
        
        for check in self.iterate_all_nodes():
            Logger.debug(f"TagTree: checking node {check.entity.text}")
            if isinstance(check, type(node)) and check.entity == node.entity:
                Logger.debug(f"TagTree: check passed. removing node.")
                self.remove_node(check)

class EntNode(GridLayout, TreeViewNode):

    def __init__(self, entity, **kwargs):
        super().__init__(**kwargs)
        if entity == None:
            Logger.warning("creating node with None entity")
        self.entity = entity
        self.load_text()
            
    def load_text(self):
        self.ids['label'].text = self.entity.text

    def copy(self):
        return EntNode(self.entity)

class SourceNode(EntNode):

    def __init__(self, entity, file, **kwargs):
        super().__init__(entity, **kwargs)
        self.file = file
    
class EntryNode(EntNode):
    
    def __init__(self, entry, file, **kwargs):
        super().__init__(entry, **kwargs)
        self.file = file
        
        if not entry.source == None:
            reference = "(" + entry.source.text
            if len(entry.page) > 0 :
                reference += ", " + entry.page
            reference += ")"
            self.ids['reference'].text = reference
        else:
            self.remove_widget(self.ids['reference'])
            
        if not entry.comment == "":
            comment = "//" + entry.comment
            self.ids['comment'].text = comment
        else:
            self.remove_widget(self.ids['comment'])

class TagNode(EntNode):

    def __init__(self, tag, controller, **kwargs):
        super().__init__(tag, **kwargs)
        self.controller = controller
        self.input = self.ids['input'].__self__
        self.label = self.ids['label'].__self__
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
        if self.editing:
            self.input.cursor = (len(self.input.text), 0)
        
    def cursor_to_start(self):
        if self.editing:
            self.input.cursor = (0, 0)
        
    def select_text(self):
        if self.editing:
            self.input.select_all()
        
    """
    These change the data based on user input
    """
    def save_text(self):
        text = self.ids['input'].text
        if text == "" or text.isspace():
            self.controller.delete_node(self)
        else:
            self.controller.edit_tag(self.entity, self.ids['input'].text)        
                
    def edit_text(self):
        self.ids['input'].text = self.entity.text