#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 12 23:04:13 2022

@author: kryis
"""

from kivy.logger import Logger

from util import CONF
from util import STRINGS
import storage.sourcefile as sourcefile
from gui.tag_tree import TagNode, SourceNode, EntryNode, TagTree

LANG = CONF["misc"]["language"]


class TagTreeController:

    def __init__(self, main_controller):
        self.main_controller = main_controller

        self.tag_file = None
        self.tag_nest = None

        # the copied tagnode; this is needed for the copy-paste functionality
        self.clipboard = None
        self._cut = False

    def set_view(self, view):
        self.view = view

    @property
    def tree(self):
        return self.view.ids['tree']

    def scroll_to(self, widget):
        if self.tree.size[1] > self.view.ids['scroll'].size[1]:
            self.view.ids['scroll'].scroll_to(widget)

    def edit_tag(self, tag, new_name):
        old_name = tag.text
        tag.text = new_name
        self.main_controller.save_file()

        if not old_name == "" and not old_name == new_name:
            func = lambda: self._edit_tag_in_files(old_name, new_name)
            self.main_controller.popup(message=STRINGS["popup"][2][LANG],
                                       callback=func)

    def _edit_tag_in_files(self, old_name, new_name):
        Logger.info(f"Controller: _edit_tag_in_files, changing {old_name} "
                    f"to {new_name}")

        for source_file in self.tag_file.source_files:
            sourcefile.edit_tag(old_name, new_name, source_file)

    def enter(self):
        selected_node = self.tree.selected_node
        if (
                isinstance(selected_node, TagNode)
                and selected_node.editing
        ):
            return
        elif isinstance(selected_node, TagNode) or selected_node is None:
            self.create_tag_at_selection()
        elif isinstance(selected_node, (EntryNode, SourceNode)):
            self.edit_node(False)

    def create_tag_at_selection(self):
        selected_node = self.tree.selected_node

        # First, change the data
        if selected_node is None or selected_node.parent_node == self.tree.root:
            parent = None
            index = -1
        else:
            parent = selected_node.parent_node.entity
            # If the selected node is not a tagnode, the new node should be
            # appended at the end of tagnodes
            if isinstance(selected_node, TagNode):
                index = parent.children.index(selected_node.entity) + 1
            else:
                index = len(parent.children)

        new_tag = self.tag_nest.create_tag(parent, index)
        self.main_controller.save_file()

        # Change the representation
        if selected_node is None or selected_node.parent_node == self.tree.root:
            parent_node = None
        else:
            parent_node = selected_node.parent_node
        new_node = TagNode(new_tag, self, self.main_controller)
        self.tree.insert_and_select(new_node, parent_node, index)

    def edit_node(self, from_end):
        """
        Switch the currently selected node to edit mode
        """
        selected_node = self.tree.selected_node
        if (
                isinstance(selected_node, TagNode)
                and not selected_node.editing
        ):
            selected_node.input_mode()
            selected_node.edit_text()
            if from_end:
                selected_node.cursor_to_end()
            else:
                selected_node.cursor_to_start()
            selected_node.select_text()
        elif isinstance(selected_node, (EntryNode, SourceNode)):
            self.main_controller.msgr.open_file(path=selected_node.file.address,
                                                item=selected_node.entity.text)

    def copy(self):
        """
        Copy the currently selected node to clipboard
        """
        if not isinstance(self.tree.selected_node, TagNode):
            self.main_controller.popup(STRINGS["popup"][6][LANG])
            return

        if self.clipboard is not None:
            self.tree.normal_color(self.clipboard)
        self.clipboard = self.tree.selected_node
        self.tree.clipboard_color(self.tree.selected_node)
        self._cut = False

    def cut(self):
        """
        Copy the currently selected node to clipboard with the flag "cut"
        """
        if not isinstance(self.tree.selected_node, TagNode):
            self.main_controller.popup(STRINGS["popup"][7][LANG])
            return

        if self.clipboard is not None:
            self.tree.normal_color(self.clipboard)
        self.clipboard = self.tree.selected_node
        self.tree.clipboard_color(self.tree.selected_node)
        self._cut = True

    # TODO: the ability to change tag order
    # TODO: enter и paste добавляют метки непонятно куда, не соблюдается индекс

    def paste(self):
        """
        Insert node from clipboard as a child to the currently selected node
        """
        selected_node = self.tree.selected_node
        if (
                selected_node is not None
                and not isinstance(selected_node, TagNode)
        ):
            self.main_controller.popup(STRINGS["popup"][0][LANG])
            return
        if self.clipboard is None:
            return
        if self.clipboard == selected_node:
            self.main_controller.popup(STRINGS["popup"][3][LANG])
            return

        # If the node is cut and no tag is selected, the node becomes a new root
        if self._cut:
            # First, changes to the data structure
            destination = None if selected_node is None else selected_node.entity
            self.tag_nest.move_tag(tag=self.clipboard.entity,
                                   destination=destination)
            self.main_controller.save_file()

            # Then, changes to the representation
            self.tree.move_node(node=self.clipboard,
                                destination=selected_node)
            self.tree.normal_color(self.clipboard)
            self.clipboard = None

        # If the node is copied and no tag is selected, nothing happens
        elif not self._cut and selected_node is not None:
            # First, change the data structure
            self.tag_nest.add_child_tag(child=self.clipboard.entity,
                                        parent=self.tree.selected_node.entity)
            self.main_controller.save_file()

            # Then, the representation
            self.tree.copy_node(node=self.clipboard,
                                destination=selected_node)
            self.tree.normal_color(self.clipboard)
            self.clipboard = None

    # TODO: changing the tag structure should apply changes to all instances of
    # the tag in the tree
    """
    Lower the level of the currently selected node (make it the child of the
    sibling that went before it)
    """
    def lower_selected_node(self):
        node = self.tree.selected_node
        if (
                node is None
                or node == self.tree.root
        ):
            return
        if not isinstance(node, TagNode):
            self.main_controller.popup(STRINGS["popup"][8][LANG])
            return

        parent = node.parent_node
        index = parent.nodes.index(node)
        if index == 0:
            self.main_controller.popup(STRINGS["popup"][4][LANG])
            return
        prev_node = parent.nodes[index - 1]

        # Change the data
        parent_tag = None if parent == self.tree.root else parent.entity
        self.tag_nest.move_tag(tag=node.entity,
                               destination=prev_node.entity,
                               former_parent=parent_tag)
        self.main_controller.save_file()

        # Change the representation
        self.tree.move_node(node, prev_node)

    """
    Increase the level of the currently selected node (make it the sibling of
    its parent)
    """

    def raise_selected_node(self):
        node = self.tree.selected_node
        if (
                node is None
                or node == self.tree.root
        ):
            return
        if not isinstance(node, TagNode):
            self.main_controller.popup(STRINGS["popup"][8][LANG])
            return
        if node.parent_node == self.tree.root:
            self.main_controller.popup(STRINGS["popup"][5][LANG])
            return
        parent = node.parent_node
        grandparent = parent.parent_node
        index = grandparent.nodes.index(parent) + 1
        if grandparent == self.tree.root:
            destination = None
        else:
            destination = grandparent.entity

        # Change the data
        self.tag_nest.move_tag(tag=node.entity,
                               destination=destination,
                               former_parent=parent.entity,
                               index=index)
        self.main_controller.save_file()

        # Change the representation
        self.tree.move_node(node, grandparent, index)

    """
    Removes the node from its current place in the tree. If that was the last
    place this tag was present in the tree, it is deleted as well.
    """

    def delete_node(self, tag_node):
        Logger.info(f"Controller: deleting node {tag_node.entity.text}")

        if len(tag_node.entity.parents) > 1:
            # If the tag still has other parents, we're just removing the link
            # to the current parent
            if tag_node.parent_node == self.tree.root:
                Logger.warning("Delete node: tag of root tree node has multiple parents")
            self.tag_nest.remove_child_tag(child=tag_node.entity,
                                           parent=tag_node.parent_node.entity)
            self.main_controller.save_file()

            self.tree.remove_node(tag_node)
        else:
            # If the tag has only one parent, we're deleting the tag
            # First, apply the changes to the data structure
            new_roots = self.tag_nest.delete_tag(tag_node.entity)
            self.main_controller.save_file()

            # Then, change the representation
            for new_root in new_roots:
                self.tree.add_node(TagNode(new_root, self, self.main_controller))
            self.tree.step_down()
            self.tree.remove_node(tag_node)

    def delete_recursively_message(self):
        node = self.tree.selected_node
        if (
                node is None
                or node == self.tree.root
        ):
            return
        if not isinstance(node, TagNode):
            self.main_controller.popup(STRINGS["popup"][10][LANG])
            return

        self.main_controller.popup(message=STRINGS["popup"][9][LANG],
                                   callback=lambda: self.delete_recursively(node))

    # TODO: should it be able to delete the tags in txt files as well? not sure
    # TODO: deleting a node does not delete other instances of that node
    def delete_recursively(self, node):
        Logger.info(f"Controller: deleting node {node.entity.text}")

        self.tag_nest.delete_tag_recursively(node.entity)
        self.main_controller.save_file()

        self.tree.remove_node(node)

    def push_node(self, forward):
        selected_node = self.tree.selected_node

        if selected_node is None or not isinstance(selected_node, TagNode):
            self.main_controller.popup(STRINGS["warning"][0])
            return

        tag = selected_node.entity

        # First, change the data
        if tag in self.tag_nest.roots:
            index = self.tag_nest.roots.index(tag)
            max_index = len(self.tag_nest.roots)
            parent = None
        else:
            parent = selected_node.parent_node.entity
            index = parent.children.index(tag)
            max_index = len(parent.children)

        if (index == 0 and not forward) or (index >= max_index - 1 and forward):
            return

        new_index = index + 1 if forward else index - 1
        self.tag_nest.move_tag(tag=tag,
                               destination=parent,
                               former_parent=parent,
                               index=new_index)

        # Then, the representation
        index = selected_node.parent_node.nodes.index(selected_node)
        new_index = index + 1 if forward else index - 1
        self.tree.move_node(node=selected_node,
                            destination=selected_node.parent_node,
                            index=new_index)
