#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 28 22:51:12 2022

@author: kryis
"""

from kivy.logger import Logger

import storage.storage as storage
import storage.parse as parse
from data.tag_nest import TagNest
from util import CONF
from util import STRINGS

LANG = CONF["misc"]["language"]


class SourceFile:

    def __init__(self, address):
        """
        This can throw an exception
        """
        # This is added so that if the address doesn't exist an exception is thrown
        open(address, "r")

        self.address = address
        self.backup_location = storage.make_backup_folder_for(address)

        self.text = ""

        # Sources and Entries present in the sourcefile
        self.sources = []
        self.entries = []
        # Tags that are encountered in the sourcefile
        self.tags = []

    def add_source(self, source):
        if source not in self.sources:
            self.sources.append(source)
        for tag in source.tags:
            if tag not in self.tags:
                self.tags.append(tag)
        for description in source.descriptions:
            self.add_entry(description)

    def add_entry(self, entry):
        if entry not in self.entries:
            self.entries.append(entry)
        for tag in entry.tags:
            if tag not in self.tags:
                self.tags.append(entry.tags)

    def read_sources(self, tag_file):
        with open(self.address, "r") as file:
            self.sources = []

            has_sources = False
            first_chunk = []

            for line in file:
                Logger.debug("read_sources: " + line[0:100])
                if parse.is_empty(line):
                    break
                else:
                    first_chunk.append(line)
                    if parse.is_source(line):
                        has_sources = True

            if has_sources:
                sources = parse.read_sources(first_chunk, tag_file.tag_nest)
                for source in sources:
                    Logger.debug(f"Sourcefile: created source {source.text[:100]}")
                    self.add_source(source)

    def read(self, tag_file):
        """
        Read the file at the address and create a sourcefile object, while also
        connecting entries and sources to specified tags if the tags are present in
        the tag nest
        """
        #TODO if the tags aren't present in the tag nest they probably should be
        # created anyway but kept in the "tags" list

        if tag_file is None:
            tag_nest = TagNest()
        else:
            tag_nest = tag_file.tag_nest

        with open(self.address, "r") as file:
            self.entries = []
            self.tags = []
            self.text = ""

            # The lines before the first empty line in a file can be sources. Split
            # the file in two halves, before the first empty line and after; if
            # the first lines are sources, read them separately; if not, add them
            # to the rest to be read as entries

            has_sources = False
            first_chunk = []
            entries = []
            after_break = False

            for line in file:
                self.text += line

                if parse.is_empty(line):
                    after_break = True
                    entries.append(line)
                elif after_break:
                    entries.append(line)
                else:
                    first_chunk.append(line)
                    if parse.is_source(line):
                        has_sources = True

            if not has_sources:
                entries = first_chunk + [parse.EMPTY_LINE] + entries

            # Read the lines as entries
            chunk = []

            def read_and_add_entry(chunk):
                all_sources = self.sources.copy()
                all_sources.extend(tag_nest.sources)
                entry = parse.read_entry(chunk,
                                         tag_nest,
                                         all_sources)
                if entry is not None:
                    #   Logger.debug(f"Sourcefile: created entry {entry.text[:100]}")
                    self.add_entry(entry)

            for line in entries:
                if parse.is_empty(line):
                    read_and_add_entry(chunk)
                    chunk = []
                else:
                    chunk.append(line)
            if not chunk == []:
                read_and_add_entry(chunk)

    def write(self, new_text):
        storage.back_up(self.address, self.backup_location)
        storage.write_safe(self.address, new_text)


def edit_tag(old_name, new_name, source_file):
    with open(source_file.address, 'r') as file:
        new_file = ""
        for line in file:
            if parse.is_enclosed(line) and old_name in line:
                #    Logger.info(f"replacing {old_name} in line {line} with " \
                #                 + f" {new_name}")
                line = line.replace(old_name, new_name)
            new_file += line
        source_file.write(new_file)


def _chunk_has_tag(tag, chunk):
    if len(chunk > 0) and tag in chunk[-1]:
        return True
    if len(chunk > 1) and tag in chunk[-2]:
        return True
    return False
