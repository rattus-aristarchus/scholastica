#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 28 22:51:01 2022

@author: kryis
"""

import collections
import os

from kivy.logger import Logger

from util import CONF, STRINGS

from data.base_types import Tag
from data.tag_nest import TagNest
import storage.storage as storage
from storage.sourcefile import SourceFile

EMPTY_LINE = "\n"
LANG = CONF["misc"]["language"]
REL_PATH_PREFIX = "rel: "
ABS_PATH_PREFIX = "abs: "
CYCLIC = " <="


class SourcePaths:

    def __init__(self, root):
        self.root = root
        self.relpaths = {}
        self.abspaths = {}

    def add(self, file):
        common_path = os.path.commonprefix([self.root, file.address])
        if common_path == "":
            self.set_abs(file, file.address)
        else:
            relpath = os.path.relpath(file.address, self.root)
            self.set_rel(file, relpath)

    def remove(self, file):
        if file in self.relpaths:
            del self.relpaths[file]
        if file in self.abspaths:
            del self.abspaths[file]

    def get_rel(self, file):
        return self.relpaths[file]

    def get_abs(self, file):
        return self.abspaths[file]

    def set_rel(self, file, path):
        self.relpaths[file] = path

    def set_abs(self, file, path):
        self.abspaths[file] = path


class TagFile:

    def __init__(self, address):
        self.address = address
        self.backup_location = storage.make_backup_folder_for(address)
        self.source_files = []
        self.source_paths = SourcePaths(os.path.dirname(address))

        self.tag_nest = TagNest()
        # self.content_by_source_file = {}

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
            self.source_paths.add(source_file)
            # contents = source_file.entries + source_file.sources
            # for content in contents:
            #    self.content_by_source_file[content] = source_file
            return True

    def remove_file(self, source_file):
        contents = source_file.sources + source_file.entries
        for content in contents:
            self.tag_nest.clear_refs(content)
            #if content in self.content_by_source_file:
            #    self.content_by_source_file.pop(content)
        source_file.sources.clear()
        source_file.entries.clear()
        if source_file in self.source_files:
            self.source_files.remove(source_file)
            self.source_paths.remove(source_file)
        else:
            Logger.warning(
                f"TagFile: trying to remove source file {source_file.address} that is not present in the list")

    def has_file(self, path):
        for source_file in self.source_files:
            if source_file.address == path:
                return True
        return False

    def get_file_with(self, content):
        for source_file in self.source_files:
            file_contents = source_file.sources + source_file.entries
            if content in file_contents:
                return source_file
        return None


def read(address):
    """
    Read a tag file and create a linked structure of tags with sources and entries
    hanging off of them.
    """
    result = TagFile(address)
    messages = []

    try:
        with open(address, "r") as file:
            # The tagfile contains first a tree of tags, and then a list of source
            # files which use the tags. Let's separate the two
            tags, source_paths = _split_tags_and_sources(file)

            # First, build the tag structure
            result.tag_nest = _build_tag_nest(tags)

            # Now, with a full structure of tags, all the sourcefiles can be read.
            # First, we create the files
            result, sf_messages = _create_source_files(result, source_paths)
            messages.extend(sf_messages)

            # Then, we read only the sources
            for source_file in result.source_files:
                source_file.read_sources(result)
                for source in source_file.sources:
                    # result.content_by_source_file[source] = source_file
                    result.tag_nest.sources.append(source)

            # Finally, we read everything else in the file
            for source_file in result.source_files:
                source_file.read(result)
                for entry in source_file.entries:
                    # result.content_by_source_file[entry] = source_file
                    result.tag_nest.entries.append(entry)

    except FileNotFoundError as e:
        Logger.error(e.strerror + ": " + e.filename)

    return result, messages


def _split_tags_and_sources(file):
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
    return tags, source_paths


def _build_tag_nest(tags):
    tag_stack = collections.OrderedDict()
    indent = 0
    parent = None
    tag_nest = TagNest()

    # In the tagfile, the innards of a tag are read only once, when it is
    # encountered for the first time
    reencounter = None

    for line in tags:
        # Based on the indent, figure out which tag the next line belongs to
        indent = _get_indent(line)
        _cut_stack(indent, tag_stack)
        if len(tag_stack) > 0:
            parent = list(tag_stack.values())[-1]
        else:
            parent = None

        if reencounter is not None and parent == reencounter:
            continue

        # Now, the string herself
        # The last symbol of the string is always a newline symbol
        string = line[indent:-1]
        # If somehow the line is empty, it is ignored
        if len(string) == 0 or string.isspace():
            continue

        # The string can either be a tag that already exists, or a new
        # one.
        tag = tag_nest.get(string)

        if tag is None:
            tag = Tag(string)
            tag_nest.tags.append(tag)
        #elif tag_nest.is_cyclic(tag, parent):
         #   continue
        else:
            reencounter = tag

        if parent is not None:
            tag_nest.add_child_tag(tag, parent)
        if indent == 0:
            tag_nest.roots.append(tag)
        tag_stack[indent] = tag

    return tag_nest


def _create_source_files(tag_file, source_paths):
    messages = []

    for line in source_paths:
        if (
                len(line) < 5
                or line.isspace()
                or tag_file.has_file(line[6:-1])
        ):
            continue
        else:
            try:
                # the first chars in a line are going to be "rel: " or "abs: "
                if line[0:5] == REL_PATH_PREFIX:
                    path = os.path.join(tag_file.source_paths.root, line[5:-1])
                elif line[0:5] == ABS_PATH_PREFIX:
                    path = line[5:-1]
                else:
                    messages.append("source begins with something other than abs or rel. source: " + line)
                    continue
                file = SourceFile(path, tag_file.backup_location)
                tag_file.source_files.append(file)
                tag_file.source_paths.add(file)
                Logger.debug("TagFile: read_tag_file, created source file " +
                             file.address)
            except FileNotFoundError as e:
                Logger.error(e.strerror + ": " + e.filename)
                message = STRINGS["error"][0][LANG][0] + \
                          e.filename + \
                          STRINGS["error"][0][LANG][1]
                messages.append(message)

    return tag_file, messages


def write(tag_file):
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
        path = _get_path(source_file, tag_file)
        if path:
            output += path + "\n"
        else:
            print("for some reason there is no path for sourcefile " + source_file.address)

    # Write the result
    storage.write_safe(tag_file.address, output)


def _get_path(source_file, tag_file):
    rel = tag_file.source_paths.get_rel(source_file)
    abs = tag_file.source_paths.get_rel(source_file)
    if not rel is None:
        output = REL_PATH_PREFIX + rel
    elif not abs is None:
        output = ABS_PATH_PREFIX + abs
    else:
        output = None
    return output


def _get_indent(line):
    """
    Determine the number of whitespaces at the beginning of the line
    """
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


def _tag_to_string_deep(tag, indent, written_tags, tag_file):
    """
    Returns the string representation of a tag, its content and its children
    """
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


def _tag_to_string(tag, indent):
    """
    Returns the string representation of a tag
    """
    result = ""
    for i in range(indent):
        result += " "
    result += tag.text + "\n"
    return result
