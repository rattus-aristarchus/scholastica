#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 11 15:35:01 2022

@author: kryis

Contains basic operations for parsing text
"""

import data.base_types as data

EMPTY_LINE = "\n"
OPEN = "("
CLOSE = ")"
SPLIT = ","


def clean_line(line):
    line = line.replace("\n", "")
    line = line.strip()
    return line


"""
Reads the chunk as an entry. If the chunk doesn't contain an entry, returns
None.
"""


def read_entry(chunk, tag_nest, sources):
    if len(chunk) == 0:
        return

    # The last lines in an entry can be a list of tags or a source, in
    # parentheses; or a comment, if the line starts with "//" or "#". First, we
    # determine which (if any) of the last lines are formatted like that.
    enclosed_lines = []
    tags = []
    source = None
    comment = ""

    for line in reversed(chunk):
        if is_enclosed(line) or is_comment(line):
            enclosed_lines.append(chunk.pop(-1))
        else:
            break

    # Then we try to get the tags, source or comment from them.
    for line in enclosed_lines:
        if is_comment(line):
            comment = get_comment(line)
        else:
            try_tags = get_tags(line, tag_nest)
            if len(try_tags) == 0:
                source = get_source(line, sources)
            else:
                tags += try_tags

    body = ""
    for line in chunk:
        body += line
    if body == "":
        return None

    # if the last symbol is a newline, we cut it away, it messes up appearance
    #   if len(body) > 1 and body[-2:] == "\n":
    #      body = body[:-2]

    result = data.Entry(body)
    if source is not None:
        result.source = source[0]
        result.page = source[1]
    for tag in tags:
        tag_nest.add_tag_to_entry(tag, result)
    result.comment = comment

    return result


"""
Returns all the tags from the tag nest that are contained in a line
"""


def get_tags(line, tag_nest):
    line = clean_line(line)[1:-1]
    names = line.split(SPLIT)
    for i in range(len(names)):
        names[i] = names[i].strip()
    tags = []
    for tag in tag_nest.tags:
        if tag.text in names:
            tags.append(tag)
    return tags


"""
Returns a source and a page from a line as a tuple
"""


def get_source(line, sources):
    line = clean_line(line)[1:-1]
    words = line.split(SPLIT)
    for i in range(len(words)):
        words[i] = words[i].strip()

    # Check if the last word is a page number
    page = ""
    if is_page(words[-1]):
        page = words.pop()

    # If the reference in parentheses is to some source that already exists in
    # the system, then it will contain only words that exist in the name of
    # that source
    for source in sources:
        contains = True
        for word in words:
            if word not in source.text:
                contains = False
                break
        if contains:
            return source, page

    # If we've not been able to find the source among existing ones, we create
    # a new one
    source = data.Source(SPLIT.join(words))
    return source, page


def get_comment(line):
    line = clean_line(line)
    if len(line) > 1 and line[0] == "#":
        line = line[1:]
    elif len(line) > 2 and line[:2] == "//":
        line = line[2:]
    return line


"""
Returns all the sources contained in a chunk, with their tags.
"""


def read_sources(chunk, tag_nest):
    result = []
    for line in chunk:
        if is_enclosed(line):
            tags = get_tags(line, tag_nest)
            for tag in tags:
                tag_nest.add_tag_to_source(tag, result[-1])
        else:
            source = data.Source(clean_line(line))
            result.append(source)
    return result


"""
Various checkers go below
"""
"""
Checks whether the line has opening and closing parentheses.
"""


def is_enclosed(line):
    to_check = clean_line(line)
    if len(to_check) == 0:
        return False
    elif to_check[0] == OPEN:
        if to_check[-1] == CLOSE:
            return True
        if to_check[-1] == "." and to_check[-2] == CLOSE:
            return True
    elif to_check[0] == "[":
        if to_check[-1] == "]":
            return True
        if to_check[-1] == "." and to_check[-2] == "]":
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


"""
Checks whether the line is the name of a source.
"""


def is_source(line):
    line = clean_line(line)
    if line[-1] == ".":
        line = line[:-1]

    if line == EMPTY_LINE or len(line) < 5:
        return False

    # Check if it's a web address
    if line[:3] == "www" or line[:4] == "http":
        return True

    words = line.split(" ")
    if len(words) == 0:
        return False

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
