#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 28 19:29:12 2022

@author: kryis
"""

class A:
    pass

a = A()
b = A()

print(isinstance(b, type(a)))