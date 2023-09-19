#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 11 15:35:01 2022

@author: kryis

Contains basic operations for parsing text
"""

from data.base_types import Tag, Entry, Source
from util import CONST, CONF

EMPTY_LINE = CONF['text']['empty_line']
OPEN = CONF['text']['line_open']
CLOSE = CONF['text']['line_close']
SPLIT = CONF['text']['split']
PARAMETER = CONF['text']['parameter_start']


def clean_line(line):
    """
    Remove newline, dots and spaces at the end of the line
    """
    line = line.replace("\n", "")
    line = line.strip()
    if len(line) > 0 and line[-1] == ".":
        line = line[:-1]
    return line


def clean_and_remove_brackets(line):
    result = clean_line(line)
    if is_enclosed(result):
        result = result[1:-1]
    return result


def clean_split(to_split, split_by):
    words = to_split.split(split_by)
    for i in range(len(words)):
        words[i] = words[i].strip()

    words = [word for word in words if not word == ""]
    return words


def add_parameters(object, parameters, tag_nest, sources=[]):
    """
    Turns parameters represented by a dictionary of strings into actual fields for the object
    """
    for parameter, value in parameters.items():
        if parameter in CONST['parameters']['source']:
            words = clean_split(value, " ")
            for i in range(len(words)):
                words[i] = words[i].strip()
            if isinstance(object, Source):
                source = get_reference_from_short_name(words, sources)
                tag_nest.add_edition(source, object)
            else:
                object.source = get_reference_from_short_name(words, sources)
        elif parameter in CONST['parameters']['subject']:
            words = clean_split(value, " ")
            source = get_reference_from_short_name(words, sources)
            tag_nest.add_description(description=object, source=source)


"""
======================================================================
Methods for reading chunks
"""


def read_sources(chunk, tag_nest):
    """
    Returns all the sources contained in a chunk, with their tags.
    """
    result = []
    for line in chunk:
        # all lines in a chunk of sources are either sources, comments,
        # or tags and parameters
        if is_enclosed(line) and len(result) > 0:
            parameters = get_parameters(line)
            add_parameters(result[-1], parameters, tag_nest)
            tags = get_tags(line, tag_nest)
            for tag in tags:
                tag_nest.add_tag_to_source(tag, result[-1])
        elif is_comment(line) and len(result) > 0:
            line = get_comment(line)
            description = Entry(line)
            result[-1].descriptions.append(description)
        else:
            source = get_source(line)
            result.append(source)
    return result


def read_entry(chunk, tag_nest, sources):
    """
    Reads the chunk of lines as an entry. If the chunk doesn't contain an entry, returns
    None.
    """
    if len(chunk) == 0:
        return

    # The last lines in an entry can be a list of tags or a source, in
    # parentheses; or a comment, if the line starts with "//" or "#". First, we
    # determine which (if any) of the last lines are formatted like that.
    enclosed_lines = []
    tags = []
    source = None
    comments = []
    parameters = {}

    for line in reversed(chunk):
        if is_enclosed(line) or is_comment(line):
            enclosed_lines.append(chunk.pop(-1))
        elif is_empty(line):
            continue
        else:
            break

    # Then we try to get the tags, source or comment from them.
    for line in enclosed_lines:
        if is_comment(line):
            comment = get_comment(line)
            comments.append(comment)
        else:
            try_parameters = get_parameters(line)
            try_tags = get_tags(line, tag_nest)
            if len(try_tags) == 0 and len(try_parameters) == 0:
                source = get_reference(line, sources)
            else:
                parameters.update(try_parameters)
                tags += try_tags

    body = ""
    for line in chunk:
        body += line
    if body == "":
        return None

    # if the last symbol is a newline, we cut it away, it messes up appearance
    #   if len(body) > 1 and body[-2:] == "\n":
    #      body = body[:-2]

    result = Entry(body)
    if source is not None:
        result.source = source[0]
        result.page = source[1]
    for tag in tags:
        tag_nest.add_tag_to_entry(tag, result)
    result.comments = comments
    add_parameters(result, parameters, tag_nest, sources)

    return result


"""
============================================================================
Methods for reading lines
"""


def get_source(line):
    """
    Reads the full name of the source and creates a source object
    """
    line = clean_and_remove_brackets(line)
    source = Source(line)

    # let's try to determine if the first words of the source are author names
    # possible scenarios:
    # surname, first letter of name, dot, possible comma
    # name, surname, dot or comma
    # surname, comma, name, dot or comma

    # TODO well, this won't be easy
    def has_type_0(words):
        if len(words) < 2:
            return False
        # surname cant end with a comma or fullstop
        if words[0][-1] in ".,":
            return False

        # the next few words can be initials
        initials = []
        for i in range(len(words) - 1):
            possible_initial = words[i+1]
            is_initial = True

            # let's run some checks
            if len(possible_initial > 4):
                # let's say that an abbreviated letter can at most be 3 characters, plus 1 for the dot
                is_initial = False
            if (
                    not possible_initial[-1] == "."
                    and not possible_initial[-2:] == ".,"
            ):
                # ...and, obviously, the inital has to end with a dot (or dot-comma)
                is_initial = False

            if is_initial:
                initials.append(possible_initial)

            # if we've encountered a word that doesn't conform to the pattern or a dot-comma,
            # it means the initals have ended
            if not is_initial or possible_initial[-2:] == ".,":
                break

        if len(initials) == 0:
            return False

        return True


#    words = line.split(" ")

 #   maybe_surname = True

  #  for word in words:
   #     if maybe_surname:

 #       elif:

    return source


def get_reference(line, sources):
    """
    Returns a source the line references and a page number as a tuple
    """
    line = clean_and_remove_brackets(line)
    words = clean_split(line, SPLIT)
    if len(words) == 0:
        return Source(""), ""

    # Check if the last word is a page number
    page = ""
    if is_page(words[-1]):
        page = words.pop()

    source = get_reference_from_short_name(words, sources)
    return source, page


def get_reference_from_short_name(words, sources):
    # If the reference in parentheses is to some source that already exists in
    # the system, then it will contain only words that exist in the name of
    # that source
    for source in sources:
        contains = True
        for word in words:
            if word[-1] == ",":
                word = word[:-1]
            if word not in source.text:
                contains = False
                break
        if contains:
            return source

    # If we've not been able to find the source among existing ones, we create
    # a new one
    source = Source(SPLIT.join(words))
    return source


def get_comment(line):
    line = clean_line(line)
    if len(line) > 1 and line[0] == "#":
        line = line[1:]
    elif len(line) > 2 and line[:2] == "//":
        line = line[2:]
    return line


def get_tags(line, tag_nest):
    """
    Returns all the tags from the tag nest that are contained in a line
    """
    line = clean_and_remove_brackets(line)
    names = clean_split(line, SPLIT)

    tags = []
    for tag in tag_nest.tags:
        if tag.text in names:
            tags.append(tag)
    return tags


def get_parameters(line):
    result = {}
    if PARAMETER not in line:
        return result
    line = clean_and_remove_brackets(line)

    # we split the line by commas and go through the resulting
    # strings - if a string contains a semicolon, it's a parameter
    strings = line.split(SPLIT)
    for string in strings:
        if PARAMETER in string:
            name_and_value = string.split(PARAMETER)
            name = clean_line(name_and_value[0])
            value = clean_line(name_and_value[1])
            result[name] = value
    return result


"""
===========================================================================================
Various checkers
"""


def is_enclosed(line):
    """
    Checks whether the line has opening and closing parentheses.
    """
    to_check = clean_line(line)
    if len(to_check) == 0:
        return False
    elif to_check[0] == OPEN and to_check[-1] == CLOSE:
        return True
    elif to_check[0] == "[" and to_check[-1] == "]":
        return True
    else:
        return False


def is_comment(line):
    to_check = clean_line(line)
    if (len(to_check) > 1 and to_check[0] == "#") \
            or (len(to_check) > 2 and to_check[:2] == "//"):
        return True
    else:
        return False


def is_page(string):
    # The string is a page if other than digits it conatins only the following
    # strings
    acceptable = [" ", "-", "pp.", "pp", "p.", "p", "стр.", "стр", "с.", "с",
                  "i", "v", "x", "c"]
    # We take out the digits and look at the strings that remain
    words = []
    word = ""
    for c in string:
        if c.isdigit() and len(word) > 0:
            words.append(word)
            word = ""
        elif not c.isdigit():
            word += c
    if len(word) > 0:
        words.append(word)

    for word in words:
        for check in acceptable:
            if check in word:
                word = word.replace(check, "")
        if len(word) > 0:
            return False

    return True


def is_source(line):
    """
    Checks whether the line is the name of a source.
    """
    line = clean_and_remove_brackets(line)

    if line == EMPTY_LINE or len(line) < 5:
        return False

    words = clean_split(line, " ")
    if len(words) == 0:
        return False

    # Check if it's a web address
    last_word = words[-1]
    if last_word[:3] == "www" or last_word[:4] == "http":
        return True

    # If the first word has a dot in it and doesn't end with a dot - it's a
    # web address; if it's longer than 5 characters - it's not an abbreviation
    if len(words[0]) > 5 and "." in words[0] and words[0][-1] != ".":
        return True

    # If the second or third character of the second word is a dot, it's most
    # likely
    # an abbreviated name, which means the whole thing is probably a source
    if len(words) > 1 and len(words[1]) > 1 and words[1][1] == ".":
        return True
    if len(words) > 1 and len(words[1]) > 2 and words[1][2] == ".":
        return True

    # If the line ends with four digits, and the character before them is not
    # a digit, this is most likely a year, and the whole thing is a source
    if line[-4:].isdigit() and not line[-5].isdigit():
        return True

    # If the line contains (ed.), (eds.), (ред.) - it's a source
    if "(ed.)" in line or "(eds.)" in line or "(ред.)" in line:
        return True

    # If the line contains "//" and it's not the first symbol, it's probably
    # the description of a journal
    if "//" in line:
        return True

    return False


def is_parameter(line):
    line = clean_and_remove_brackets(line)

    if CONF['text']['parameter_start'] in line:
        return True
    else:
        return False

    # TODO: maybe add a check confirming that the next symbol after the semicolon is a whitespace?


def is_empty(line):
    line = line.replace("\\n", "")
    line = line.replace("\\r", "")
    if line.isspace() or len(line) == 0:
        return True
    else:
        return False
