#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 28 22:51:01 2022

@author: kryis
"""

import collections
from kivy.logger import Logger

from util import CONF, STRINGS

from data.base_types import Tag
from data.tag_nest import TagNest
import storage.storage as storage
from storage.sourcefile import SourceFile

EMPTY_LINE = "\n"
LANG = CONF["misc"]["language"]


class TagFile:

    def __init__(self, address):
        self.address = address
        self.backup_location = storage.make_backup_folder_for(address)
        self.source_files = []

        self.tag_nest = TagNest()
        self.content_by_source_file = {}

    def add_file(self, source_file):
        """
        Add a link to a new source file.

        returned value: boolean, whether the operation to add was necessary.
        """
        # TODO: should a call to write file be part of those?
        if self.has_file(source_file.address):
            return False
        elif len(source_file.tags) == 0:
            return False
        else:
            self.source_files.append(source_file)
            contents = source_file.entries + source_file.sources
            for content in contents:
                self.content_by_source_file[content] = source_file
            return True

    def remove_file(self, source_file):
        contents = source_file.sources + source_file.entries
        for content in contents:
            self.tag_nest.clear_refs(content)
            if content in self.content_by_source_file:
                self.content_by_source_file.pop(content)
        source_file.sources.clear()
        source_file.entries.clear()
        if source_file in self.source_files:
            self.source_files.remove(source_file)
        else:
            Logger.warning(
                f"TagFile: trying to remove source file {source_file.address} that is not present in the list")

    def has_file(self, path):
        for source_file in self.source_files:
            if source_file.address == path:
                return True
        return False


# TODO: make this a proper class. the procedural approach looks hideous when you have
# to call the functions - tagfile.read_tag_file(tag_file)


def read_tag_file(address):
    """
    Read a tag file and create a linked structure of tags with sources and entries
    hanging off of them.
    """
    result = TagFile(address)
    messages = []

    try:
        with open(address, "r") as file:

            indent = 0
            tag_stack = collections.OrderedDict()
            parent = None

            # The tagfile contains first a tree of tags, and then a list of source
            # files which use the tags
            tags = []
            source_paths = []
            after_break = False
            for line in file:
                if line == CONF["text"]["separator"] + "\n":
                    after_break = True
                elif not after_break:
                    tags.append(line)
                else:
                    source_paths.append(line)

            # First, build the tag structure
            for line in tags:
                # Based on the indent, figure out which tag the next line belongs to
                indent = _get_indent(line)
                _cut_stack(indent, tag_stack)
                if len(tag_stack) > 0:
                    parent = list(tag_stack.values())[-1]
                else:
                    parent = None

                # Now, the string herself
                # The last symbol of the string is always a newline symbol
                string = line[indent:-1]
                # If somehow the line is empty, it is ignored
                if len(string) == 0 or string.isspace():
                    continue

                # The string can either be a tag that already exists, or a new
                # one.
                tag = result.tag_nest.get(string)
                if tag is None:
                    tag = Tag(string)
                    result.tag_nest.tags.append(tag)
                if parent is not None:
                    result.tag_nest.add_child_tag(tag, parent)
                if indent == 0:
                    result.tag_nest.roots.append(tag)
                tag_stack[indent] = tag

            # Now, with a full structure of tags, all the sourcefiles can be read.
            # First, we create the files
            for line in source_paths:
                if (
                        len(line) == 0
                        or line.isspace()
                        or result.has_file(line[:-1])
                ):
                    continue
                else:
                    try:
                        file = SourceFile(line[:-1], result.backup_location)
                        result.source_files.append(file)
                    except FileNotFoundError as e:
                        Logger.error(e.strerror + ": " + e.filename)
                        message = STRINGS["error"][0][LANG][0] + \
                                    e.filename + \
                                    STRINGS["error"][0][LANG][1]
                        messages.append(message)

            # Then, we read only the sources
            for source_file in result.source_files:
                source_file.read_sources(result)
                for source in source_file.sources:
                    result.content_by_source_file[source] = source_file
                    result.tag_nest.sources.append(source)

            # Finally, we read everything else in the file
            for source_file in result.source_files:
                source_file.read(result)
                for entry in source_file.entries:
                    result.content_by_source_file[entry] = source_file
                    result.tag_nest.entries.append(entry)

    except FileNotFoundError as e:
        Logger.error(e.strerror + ": " + e.filename)

    return result, messages


def write_tag_file(tag_file):
    """
    Write a linked structure of tags with their contents as a file.
    """
    output = ""
    indent = 0
    written_tags = []

    storage.back_up(tag_file.address, tag_file.backup_location)

    # Traverse the roots; for each of them call a recursive function to get
    # their string representation
    for root in tag_file.tag_nest.roots:
        output += _tag_to_string_deep(root,
                                      indent,
                                      written_tags,
                                      tag_file)

    # Add the sources
    output += EMPTY_LINE
    output += CONF["text"]["separator"] + "\n"
    for source_file in tag_file.source_files:
        output += source_file.address + "\n"

    # Write the result
    storage.write_safe(tag_file.address, output)


"""
Determine the number of whitespaces at the beginning of the line
"""


def _get_indent(line):
    spaces = 0
    for c in line:
        if c.isspace():
            spaces += 1
        else:
            break
    return spaces


def _cut_stack(cur_indent, stack):
    for indent in list(stack):
        if indent >= cur_indent:
            stack.pop(indent)


"""
Returns the string representation of a tag, its content and its children
"""


def _tag_to_string_deep(tag, indent, written_tags, tag_file):
    # First, the tag itself
    result = _tag_to_string(tag, indent)

    # Then, its content and children, recursively - unless they've already been
    # written down elsewhere in the file
    if tag not in written_tags:
        written_tags.append(tag)
        for child in tag.children:
            result += _tag_to_string_deep(child,
                                          indent + 4,
                                          written_tags,
                                          tag_file)
    return result


"""
Returns the string representation of a tag
"""


def _tag_to_string(tag, indent):
    result = ""
    for i in range(indent):
        result += " "
    result += tag.text + "\n"
    return result
