#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 11 15:35:01 2022

@author: kryis

Contains basic operations for parsing text
"""

import data

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
def read_entry(chunk, all_tags, sources):
    if len(chunk) == 0:
        return
    
    #The last two lines in an entry can be a list of tags or a source, in 
    #parentheses. First, we determine if the last or the last two lines have
    #parentheses.
    enclosed_lines = []
    tags = []
    source = None
    if is_enclosed(chunk[-1]):
        enclosed_lines.append(chunk.pop(-1))
        
        if len(chunk) > 0 and is_enclosed(chunk[-1]):
            enclosed_lines.append(chunk.pop(-1))
    
    #Then we try to get the tags and source from them.
    for line in enclosed_lines:
        try_tags = get_tags(line, all_tags)
        if len(try_tags) == 0:
            source = get_source(line, sources)
        else:
            tags += try_tags
    
    body = ""
    for line in chunk:
        body += line
    if body == "":
        return None
    
    result = data.Entry(body)
    if source != None:
        result.source = source[0]
        result.page = source[1]
    for tag in tags:
        data.add_tag_to_entry(tag, result)

    return result

"""
Returns all the tags from the tag nest that are contained in a line
"""
def get_tags(line, all_tags):
    line = clean_line(line)[1:-1]
    names = line.split(SPLIT)
    for i in range(len(names)):
        names[i] = names[i].strip()
    tags = []
    for tag in all_tags:
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
        
    #Check if the last word is a page number
    page = 0
    if words[-1].isdigit():
        page = words.pop()
    
    #If the reference in parentheses is to some source that already exists in
    #the system, then it will contain only words that exist in the name of 
    #that source
    for source in sources:
        contains = True
        for word in words:
            if not word in source.text:
                contains = False
                break
        if contains:
            return (source, page)
    
    #If we've not been able to find the source among existing ones, we create
    #a new one
    source = data.Source("".join(words))
    return (source, page)

"""
Returns all the sources contained in a chunk, with their tags.
"""
def read_sources(chunk, all_tags):
    result = []
    for line in chunk:
        if is_enclosed(line):
            tags = get_tags(line, all_tags)
            for tag in tags:
                data.add_tag_to_source(tag, result[-1])
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
    if len(to_check) > 0 and to_check[0] == OPEN and to_check[-1] == CLOSE:
        return True
    return False

#TODO: номер страницы может быть римскими цифрами

def is_page(string):
    #The string is a page if other than digits it conatins only the following
    #strings
    acceptable = [" ", "-", "pp.", "pp", "p.", "p", "стр.", "стр", "с.", "с"]
    #We take out the digits and look at the strings that remain
    words = []
    word = ""
    for c in string:
        if c.isdigit():
            words.append(word)
            word = ""
        else:
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
        
    #Check if it's a web address
    if line[:3] == "www" or line[:4] == "http":
        return True
    
    words = line.split(" ")
    if len(words) == 0:
        return False
    
    #If the first word has a dot in it and doesn't end with a dot - it's a
    #web address; if it's longer than 5 characters - it's not an abbreviation
    if len(words[0]) > 5 and "." in words[0] and words[0][-1] != ".":
        return True
    
    #If the second or third character of the second word is a dot, it's most 
    # likely
    #an abbreviated name, which means the whole thing is probably a source
    if len(words) > 1 and len(words[1]) > 1 and words[1][1] == ".":
        return True
    if len(words) > 1 and len(words[1]) > 2 and words[1][2] == ".":
        return True
    
    #If the line ends with four digits, and the character before them is not
    #a digit, this is most likely a year, and the whole thing is a source
    if line[-4:].isdigit() and not line[-5].isdigit():
        return True
    
    #If the line contains (ed.), (eds.), (ред.) - it's a source
    if "(ed.)" in line or "(eds.)" in line or "(ред.)" in line:
        return True
    
    #If the line contains "//" and it's not the first symbol, it's probably
    #the description of a journal
    if "//" in line:
        return True
    
    return False