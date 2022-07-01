#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 27 18:34:31 2022

@author: kryis
"""

import sys
sys.path.insert(0, "/media/kryis/TOSHIBA EXT/code/Python/scholastica/src")

import src.storage.tagfile as tgf
import src.storage.sourcefile as srf
import data

def check_tag_parser():
    tag_line_0 = " (first_tag, second_tag) \n"
    tag_line_1 = "     (;afkaj;fdjasdfl1342-`-0)\n"
    not_tag_line_0 = "asdl;kfjasjlkf;akwe\n"
    assert srf._is_enclosed(tag_line_0)
    first_tag = data.Tag("first_tag")
    assert srf._get_tags(tag_line_0, [first_tag])[0] == first_tag
    assert srf._is_enclosed(tag_line_1)
    assert not srf._is_enclosed(not_tag_line_0)
    print("check_tag_parser - done")

def check_source():
    l0 = "Levin, S. A. (ed.), Princeton guide to ecology. Princeton Univ. Press. Part VII Managing the Biosphere"
    l1 = "Stevenson D. S. Under a Crimson Sun: Prospects for Life in a Red Dwarf System. Springer, 2013."
    l2 = "все дальнейшие рассуждения, если без ссылок - с вики про возможность жизни на др планетах"
    l3 = "Waltham T., Bell F., Culshaw M. Sinkholes and Subsistence. Karst and Cavernous Rocks in Engineering and COnstruction"
    assert srf._is_source(l0)
    assert srf._is_source(l1)
    assert not srf._is_source(l2)
    assert srf._is_source(l3)
    print("check_source - done")

def check_page():
    s0 = "стр. 0"
    s1 = "1"
    s2 = "asdf"
    s3 = "pp.100-101"
    assert srf._is_page(s0)
    assert srf._is_page(s1)
    assert not srf._is_page(s2)
    assert srf._is_page(s3)
    print("check_page - done")
    
print('begin')
check_tag_parser()
check_source()
check_page()