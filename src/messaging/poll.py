#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: kryis

This module connects the text editor plugin to the main application. It was 
created because at first I was reluctant to use rpcs for that purpose. The
module uses temporary text files to leave messages to and from the plugin. 
Currently it is not finished because it turned out using rpcs is easier.
"""

import os 
import time
import threading


POLLED_FILE = ".scholastica_source"

SEPARATOR = ":"
MSG_SAVE = "FILE SAVED"

class Messenger(threading.Thread):
    
    def __init__(self, msg_save, root):
        super().__init__()
        self.msg_save = msg_save
        self.root = root
        self.monitored_files = []

    def read_message(self, message):
        message = message.replace("\n", "")
        #Extract message type and content from the string
        if SEPARATOR in message:
            sep = message.index(SEPARATOR)
            msg_type = message[:sep]
            if sep < len(message):
                msg_content = message[sep + 1:]
            else:
                msg_content = ""
        else:
            msg_type = message
            msg_content = ""
            
        if MSG_SAVE in msg_type:
            self.msg_save(msg_content)
        
    
    """
    hopefully this will never have to be used
    """
    def traverse(self, directory):
        files = []
        for obj in os.listdir(directory):
            if os.path.isfile(obj):
                if POLLED_FILE in obj:
                    files.append(obj)
            elif os.path.isdir(obj):
                files = files + self.traverse(obj)
        return files
    
    def synch(self, paths, files):
        for path in paths:
            present = False
            for file in self.monitored_files:
                if file.path == path:
                    present = True
                    break
                
            if not present:
                files.append(Input(path))
                
            #TODO: then we also have to figure out which files don't have corresponding paths
        
     
    def run(self):       
        last_size = 0
        last_line = 0
        
        while True:
            time.sleep(1)
            files = self.traverse(self.root)
            new_size = os.path.getsize(self.location)
            if new_size > last_size:
                last_size = new_size
                with open(self.location, "r") as file:
                    all_lines = file.readlines()
                    new_lines = all_lines[last_line:]
                    last_line = len(all_lines)
                    for line in new_lines:
                        self.read_message(line)
                        
class Input:
    
    def __init__(self, path):
        self.path = path
        self.last_size = 0
        self.last_line = 0