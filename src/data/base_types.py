#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
The basic data structures.

Created on Fri May 27 14:30:56 2022

@author: kryis
"""


class Tag:
    """
    Tags are used to organize entries and sources. Tags form a directed graph.
    Every tag can have parent tags and child tags. The "content" variable lists
    all the Entries and Sources attached to the tag.
    """

    def __init__(self, text=""):
        self.text = text
        self.parents = []
        self.children = []
        # The sources and entries which have the tag
        self.content = []

    # I am defining the eq and hash methods so that the "in" keyword will be
    # able to tell if the tag is present in a list of tags
    def __eq__(self, o):
        return isinstance(o, Tag) and self.text == o.text

    def __hash__(self):
        return hash(self.text)


class Entry:
    """
    A piece of text with a reference to a source and tags attached to it.
    """

    #  Which makes me think. Ideally, data should only be stored once, in one
    # place. Maybe the "tags" variables from Entry and Source should be deleted?

    def __init__(self, text):
        self.text = text
        self.comments = []
        self.tags = []
        self.source = None
        self.page = ""
        self.subjects = []


class Source:
    def __init__(self, text):
        self.text = text
        self.tags = []
        self.descriptions = []
        self.editions = []
        self.source = None

    def get_first_word(self):
        word = ""
        for char in self.text:
            if char in " ,.;:-=":
                break
            else:
                word += char
        return word

    def __eq__(self, o):
        return isinstance(o, Source) and self.text == o.text

    def __hash__(self):
        return hash(self.text)
