#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 18 15:21:35 2022

@author: kryis
"""


import sys
sys.path.insert(0, "/home/kryis/code/python/scholastica/")
import src.storage.tagfile as tagfile
import src.storage.sourcefile as sourcefile


class TestMain:
    
    def __init__(self, tag_file):
        self.tag_file = tag_file

    def file_saved(self, path):
        print("Message received: " + path)
        #First, we check if the file is one of those already tracked by the 
        #application. If it is, all its content is reloaded.
        existing = None
        for check in self.tag_file.source_files:
            print("checking " + check.address)
            if check.address == path:
                existing = check
                break
        print("-a")
                
        if not existing == None:
            #If it does exist:
            print("a")
            sourcefile.clean()
            self.tag_file.source_files.remove(existing)
            source_file = sourcefile.read(path, self.tag_file.tag_nest)
            if len(source_file.tags) > 0:
                print("b")
                self.tag_file.source_files.append(source_file)
            tagfile.write_tag_file(self.tag_file)
        else:
            #If it doesn't, we read the file and see if it has any tags at all
            print("-c")
            source_file = sourcefile.read(path, self.tag_file.tag_nest)
            print("c")
            if len(source_file.tags) > 0:
                print("d")    
                self.tag_file.source_files.append(source_file)
            tagfile.write_tag_file(self.tag_file)
            
        return ""


# def test_rpc():
#    address = "/media/kryis/TOSHIBA EXT/записи/организатор записей/тестовый файл.txt"
#    file = tagfile.read_tag_file(address)
#    test_main = TestMain(file)
#    messenger = rpc.Messenger(test_main.file_saved)
#    messenger.run()
 
    
#test_rpc()