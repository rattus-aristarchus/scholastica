#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun  5 16:19:01 2022

@author: kryis
"""

from kivy.clock import Clock
from kivy.logger import Logger
from kivy.uix.treeview import TreeView, TreeViewNode, TreeViewLabel
from kivy.properties import ObjectProperty

from data.base_types import Source
from data.base_types import Entry
from util import CONF
from util import CONST
from gui.tree_nodes import EntNode, SourceNode, EntryNode, TagNode, JumpNode

LOAD_DEPTH = CONF["misc"]["load_depth"]

LANG = CONF["misc"]["language"]
THEME = CONF["misc"]["theme"]


class TagTree(TreeView):
    """
    The visual representation of a TagNest. Synchronization with the tagnest should
    happen elsewhere, this just provides the basic methods for manipulating the
    tree.
    """

    controller = ObjectProperty()
    main_controller = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(root_options=dict(text='Гнездо'), **kwargs)
        self.bind(minimum_height=self.setter("height"))

        self.tag_file = None
        self.tag_nest = None

    def clear(self):
        """
        Remove all content.
        """
        for node in [i for i in self.iterate_all_nodes()]:
            self.remove_node(node)

    def show(self, tag_file):
        """
        Traverse all the roots in the nest recursively and add them to the
        tree.
        """
        Logger.info(f"TagTree: showing tag file {tag_file.address}")

        self.tag_file = tag_file
        self.tag_nest = tag_file.tag_nest
        for root_tag in tag_file.tag_nest.roots:
            self._show_deep(root_tag, None, [])

    # TODO: change functions such as _show_deep into internal functions of their
    # parent function. it's gonna be moe logical since they have no use outside
    # their parent anyway

    def _show_deep(self, tag, parent_node, parents):
        # To avoid cycles in our tree we stop the traversion if the tag is
        # already present among its parents or grandparents of any level.
        if (
                tag in parents
                or (
                    not parent_node is None
                    and tag == parent_node.entity
                )
        ):
            return

        # Display the tag itself
        tag_node = TagNode(tag, self.controller, self.main_controller)
        if parent_node is None:
            self.add_node(tag_node)
        else:
            self.add_node(tag_node, parent_node)
        if len(parents) >= LOAD_DEPTH:
            tag_node.load_point = True

        # Repeat the function for all of its children; do not load the tree beyond a certain depth, unless this
        # has been specifically requested
        if len(tag.children) > 0 and len(parents) < LOAD_DEPTH:
            parents.append(tag)
            for child in tag.children:
                self._show_deep(child, tag_node, parents)
            parents.remove(tag)

        # Display other parents of this tag
        for parent in tag.parents:
            if not parent == parent_node.entity:
                self.display_jump_node(parent, tag_node)

        # Display all sources with the tag
        for content in tag.content:
            if isinstance(content, Source):
                self.display_source(content, tag_node)

        # Display all entries
        for content in tag.content:
            if isinstance(content, Entry):
                self.display_entry(content, tag_node)

    def remove_all_from(self, source_file):
        """
        Remove all nodes corresponding to entities contained in the source file.
        """
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

    def add_all_from(self, source_file):
        """
        Add new nodes for every entity in the source file
        """
        Logger.info(f"TagTree: adding source file {source_file.address}")

        for source in source_file.sources:
            for tag in source.tags:
                parent_nodes = self._find_nodes(tag)
                if len(parent_nodes) > 0:
                    for parent_node in parent_nodes:
                        self.display_source(source, parent_node)
                else:
                    Logger.warning(f"source {source.text} has a tag {tag.text}"
                                   + f" that is not present on the tag tree")

        for entry in source_file.entries:
            parents = entry.tags + entry.subjects
            for parent in parents:
                parent_nodes = self._find_nodes(parent)
                if len(parent_nodes) > 0:
                    for parent_node in parent_nodes:
                        self.display_entry(entry, parent_node)
                else:
                    Logger.warning(f"entry {entry.text} has a tag or description "
                                   f"{parent.text} that is not present on the tag tree")

    def _find_nodes(self, entity):
        result = []
        for node in list(self.iterate_all_nodes()):
            if isinstance(node, EntNode) and node.entity.text == entity.text:
                result.append(node)
        return result

    def display_source(self, source, parent_node):
        file = self.tag_file.get_file_with(source)
        if file is None:
            Logger.error("TagTree: display_source, source " + source.text +
                         " is not found in any file")
        source_node = SourceNode(source, file)
        self.add_source_node(source_node, parent_node)
        for edition in source.editions:
            self.display_source(edition, source_node)
        for description in source.descriptions:
            self.display_entry(description, source_node)

    def display_entry(self, entry, parent_node):
        file = self.tag_file.get_file_with(entry)
        if file is None:
            Logger.error("TagTree: display_entry, entry " + entry.text +
                         " is not found in any file")
        entry_node = EntryNode(entry, file)
        self.add_node(entry_node, parent_node)

    def display_jump_node(self, jump_to, parent_node):
        jump_to_node = JumpNode(jump_to, self.controller, self.main_controller)
        self.add_tag_node(jump_to_node, parent_node)
        dummy_node = TreeViewLabel()
        self.add_node(dummy_node, jump_to_node)

    def add_tag_node(self, tag_node, destination):
        """
        Inserts a tag node before all content nodes at the destination
        """
        if destination is None:
            destination = self.root

        index = len(destination.nodes)
        for node in destination.nodes:
            if not isinstance(node, TagNode):
                index = destination.nodes.index(node)
                break
        self.insert_node(tag_node, destination, index)

    # TODO: check border cases for all functions and provide error messages

    def add_source_node(self, source_node, destination):
        """
        Inserts a source node before entries but after tags at destination
        """
        if destination is None:
            destination = self.root

        index = len(destination.nodes)
        for node in destination.nodes:
            if not isinstance(node, (TagNode, SourceNode)):
                index = destination.nodes.index(node)
                break
        self.insert_node(source_node, destination, index)

    def insert_node(self, node, parent, index):
        """
        Inserts a node among the children of the specified parent at the index
        """
        parent_name = "root" if parent == self.root else parent.entity.text
        Logger.info("TagTree: insert node at index " + str(index) +
                    ", node " + node.entity.text[:50] + ", parent " +
                    parent_name)
        if node == self.root:
            Logger.warning(f"INSERT NODE: trying to insert root node into "
                           f"node {parent.entity.text} at index {index}")
            return
        if index > len(parent.nodes):
            Logger.warning(f"INSERT NODE: index too large, inserting node "
                           f"{node.entity.text} into parent "
                           f"{parent.entity.text} at index {index} while the"
                           f"parent only has {len(parent.nodes)} children")
            return

        # Remove all nodes after node_after
        after_node = parent.nodes[index:]
        for next_node in after_node:
            Logger.debug("TagTree: removing node " + next_node.entity.text[:50] + "; to be re-added later")
            self.remove_node(next_node)

        # Add the inserted node and then put back all the nodes removed before
        Logger.debug("TagTree: adding the node")
        self.add_node(node, parent)
        for next_node in after_node:
            Logger.debug("TagTree: re-adding removed node " + next_node.entity.text[:50])
            self.add_node(next_node, parent)

    # TODO: this does not remove all instances for some reason
    def remove_all_instances(self, node):
        if node == self.root:
            return
        Logger.info(f"TagTree: removing instances of node {node.entity.text}")

        for check in self.iterate_all_nodes():
            Logger.debug(f"TagTree: checking node {check.entity.text}")
            if isinstance(check, type(node)) and check.entity == node.entity:
                Logger.debug(f"TagTree: check passed. removing node.")
                self.remove_node(check)

    def step_down(self):
        """
        Select next node
        """
        if self.selected_node is None:
            if len(self.root.nodes) > 0:
                self._select_and_scroll(self.root.nodes[0])
        elif self.selected_node.is_leaf or not self.selected_node.is_open:
            self._traverse_down(self.selected_node)
        else:
            self._select_and_scroll(self.selected_node.nodes[0])

    def step_down_over(self):
        """
        Select next node, stepping over lower-level nodes
        """
        if self.selected_node is None:
            if len(self.root.nodes) > 0:
                self._select_and_scroll(self.root.nodes[0])
        else:
            self._traverse_down(self.selected_node)

    # TODO this should return the value, not do it herself
    def _traverse_down(self, cur_node):
        parent = cur_node.parent_node
        if parent is None:
            self.deselect_node(self.selected_node)
            return

        index = parent.nodes.index(cur_node)

        if index < len(parent.nodes) - 1:
            self._select_and_scroll(parent.nodes[index + 1])
        else:
            self._traverse_down(parent)

    def step_up(self):
        """
        Select previous node
        """
        self._step_up(False)

    def step_up_over(self):
        """
        Select previous node, stepping over lower-level nodes
        """
        self._step_up(True)

    def _step_up(self, over):
        if self.selected_node is None or self.selected_node == self.root:
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

    def step_out(self):
        """
        Select the parent of current node and collapse the current node
        """
        if self.selected_node is None:
            return

        if self.selected_node.is_open:
            self.toggle_node(self.selected_node)
        elif (
                isinstance(self.selected_node, EntryNode)
                and self.selected_node.full_text is True
        ):
            self.selected_node.full_text = False
            self.selected_node.load_text()
        else:
            parent = self.selected_node.parent_node
            if not parent == self.root or parent is None:
                self.toggle_node(parent)
                self._select_and_scroll(parent)

    def step_in(self):
        """
        Expand current node and select its first child
        """
        select = self.selected_node

        # If it's a jump node, we need to change the focus to the node it points toward
        if isinstance(select, JumpNode):
            nodes = self._find_nodes(select.entity)
            if len(nodes) == 0:
                Logger.error(f"JumpNode with parent {select.parent_node.entity} links"
                             f" to a node {select.entity.text} that is missing from the tree")
            for node in nodes:
                if not isinstance(node, JumpNode):
                    self._select_and_scroll(node)
                    break
        elif (
                not select is None
                and not select.is_leaf
                and not select.is_open
        ):
            # If it's a load point, we've got to load a new chunk of nodes
            if isinstance(select, TagNode) and select.load_point:
                for tag in select.entity.children:
                    self._show_deep(tag, select, [])
                select.load_point = False
                #TODO: for some reason, in the load point tag child content is loaded first and the tags next

            self.toggle_node(select)
            self.step_down()
        elif isinstance(select, EntryNode) and not select.full_text:
            select.full_text = True
            select.load_text()

    def insert_and_select(self, node, parent, index):
        """
        Add a new child node to the parent of currently selected node
        """
        Logger.info("TagTree: insert_and_select")
        if parent is None:
            Logger.debug("TagTree: adding new root node")
            self.add_node(node)
        elif index == -1:
            Logger.debug("TagTree: appending new node at node " + parent.entity.text)
            self.add_tag_node(node, parent)
        else:
            Logger.debug("TagTree: inserting new node at node " + parent.entity.text + " at index " + str(index))
            self.insert_node(node, parent, index)

        if parent is not None and parent.is_open is not True:
            Logger.debug("TagTree: expanding the parent node")
            parent.is_open = True

        def edit(dt):
            self._select_and_scroll(node)
            self.controller.edit_node(False)

        Clock.schedule_once(edit, 0.1)

    def move_node(self, node, destination, index=-1):
        self.remove_node(node)
        if index == -1:
            self.add_tag_node(node, destination)
        else:
            self.insert_node(node, destination, index)

        if destination is not None:
            destination.is_open = True

        Clock.schedule_once(lambda dt: self._select_and_scroll(node), 0.1)

    def copy_node(self, node, destination):
        if node.parent_node == self.root:
            self.remove_node(node)

        new_node = self._copy_node(node, destination)

        if destination is not None:
            destination.is_open = True
        self._select_and_scroll(new_node)

    def _copy_node(self, node, destination):
        new_node = node.copy()
        if isinstance(node, TagNode):
            self.add_tag_node(new_node, destination)
        elif isinstance(node, SourceNode):
            self.add_source_node(new_node, destination)
        else:
            self.add_node(node, destination)

        for child in node.nodes:
            self._copy_node(child, new_node)
        return new_node

    def clipboard_color(self, node):
        node.even_color = CONST[THEME]["clipboard_background"]
        node.odd_color = CONST[THEME]["clipboard_background"]

    def normal_color(self, node):
        node.even_color = CONST[THEME]["tag_background"]
        node.odd_color = CONST[THEME]["tag_background"]

    def change_text_for_all_nodes(self, old_text, new_text):
        for node in self.iterate_all_nodes():
            if isinstance(node, EntNode) and node.ids['label'].text == old_text:
                node.ids['label'].text = new_text
