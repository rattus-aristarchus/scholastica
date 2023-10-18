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

        self.sources = []
        self.entries = []

    def get(self, name):
        """
        Finds a tag with the specified name.
        """
        for tag in self.tags:
            if tag.text == name:
                return tag
        return None

    def add_tag_to_source(self, tag, source):
        if tag not in source.tags:
            source.tags.append(tag)
        if source not in tag.content:
            tag.content.append(source)

    def add_tag_to_entry(self, tag, entry):
        if tag not in entry.tags:
            entry.tags.append(tag)
        if entry not in tag.content:
            tag.content.append(entry)

    def remove_tag_from_content(self, tag, content):
        if tag in content.tags:
            content.tags.remove(tag)
        if content in tag.content:
            tag.content.remove(content)

    def add_child_tag(self, child, parent=None, index=-1):
        if parent is None:
            if index == -1:
                self.roots.append(child)
            else:
                self.roots.insert(index, child)
        else:
            if child not in parent.children:
                if index == -1:
                    parent.children.append(child)
                else:
                    parent.children.insert(index, child)
            if parent not in child.parents:
                child.parents.append(parent)
         #   if self.is_cyclic(child, parent):
         #       child.cyclic = True

    def remove_child_tag(self, child, parent):
        """
        Does not make the new child a root if it has no other parents.
        """
        if parent in child.parents:
            child.parents.remove(parent)
        if child in parent.children:
            parent.children.remove(child)

    def create_tag(self, parent, name="", index=-1):
        new_tag = Tag(name)
        self.tags.append(new_tag)

        # If no node is selected, the new node becomes a root
        if parent is None:
            self.roots.append(new_tag)
        else:
            self.add_child_tag(new_tag, parent, index)

        return new_tag

    def move_tag(self, tag, destination, former_parent=None, index=-1):
        if tag in self.roots:
            self.roots.remove(tag)
        elif former_parent is None:
            for parent in tag.parents:
                self.remove_child_tag(tag, parent)
        else:
            self.remove_child_tag(tag, former_parent)

        self.add_child_tag(tag, destination, index)

    def delete_tag(self, tag):
        """
        Delete the tag. Returns a list of child tags that have become new roots
        """
        # Find the nodes whose tags have only one parent. Those are added to
        # the nest as new roots
        new_roots = []
        for child in tag.children:
            if len(child.parents) < 2:
                new_roots.append(child)
        self.roots += new_roots

        # Remove all references to the deleted tag
        self.clear_refs(tag)

        return new_roots

    def delete_tag_recursively(self, tag):
        """
        Delete the tag and all its children that have only one parent, recursively.
        """
        for child in tag.children:
            if len(child.parents) == 1:
                self.delete_tag_recursively(child)
            else:
                self.remove_child_tag(child, tag)
        self.clear_refs(tag)

    def clear_refs(self, entity):
        if isinstance(entity, Entry):
            if entity in self.entries:
                self.entries.remove(entity)
            for tag in entity.tags:
                if entity in tag.content:
                    tag.content.remove(entity)

        elif isinstance(entity, Source):
            if entity in self.sources:
                self.sources.remove(entity)
            for tag in entity.tags:
                if entity in tag.content:
                    tag.content.remove(entity)

        elif isinstance(entity, Tag):
            self.tags.remove(entity)
            for content in entity.content:
                content.tags.remove(entity)
            for tag in entity.parents:
                tag.children.remove(entity)
            for tag in entity.children:
                tag.parents.remove(entity)
            if entity in self.roots:
                self.roots.remove(entity)

    def add_description(self, description, source):
        if description not in source.descriptions:
            source.descriptions.append(description)
        if source not in description.subjects:
            description.subjects.append(source)

    def add_edition(self, source, edition):
        if edition not in source.editions:
            source.editions.append(edition)
        edition.source = source

    def is_cyclic(self, tag, parent):
        """
        Check if adding the tag to the parent creates a cyclic tree structure
        """
        if tag == parent:
            return True

        if not parent is None and self._parents_have_tag(tag, parent):
            return True

        return False

    def _parents_have_tag(self, tag, to_check):
        """
        Check if parents of any generation of @to_check contain @tag
        """

        if tag in to_check.parents:
            return True

        for parent in to_check.parents:
            if self._parents_have_tag(tag, parent):
                return True

        return False
