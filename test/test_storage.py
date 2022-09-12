#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 27 18:34:31 2022

@author: kryis
"""

import sys

import allure

sys.path.insert(0, "/home/kryis/code/python/scholastica/src")

import storage.tagfile as tgf
import storage.sourcefile as srf
import storage.parse as parse
import data.base_types as data
from data.tag_nest import TagNest


class TestParse:

    def setup(self):
        pass

    def teardown(self):
        pass

    @allure.story('Parsing tags')
    @allure.severity('critical')
    def test_tag_parser(self):
        tag_line_0 = " (first_tag, second_tag) \n"
        tag_line_1 = "     (;afkaj;fdjasdfl1342-`-0)\n"
        not_tag_line_0 = "asdl;kfjasjlkf;akwe\n"
        assert parse.is_enclosed(tag_line_0)
        first_tag = data.Tag("first_tag")
        nest = TagNest()
        nest.tags = [first_tag]
        assert parse.get_tags(tag_line_0, nest)[0] == first_tag
        assert parse.is_enclosed(tag_line_1)
        assert not parse.is_enclosed(not_tag_line_0)

    @allure.story('Parsing sources')
    @allure.severity('blocker')
    def test_source(self):
        l0 = "Levin, S. A. (ed.), Princeton guide to ecology. Princeton Univ. Press. Part VII Managing the Biosphere"
        l1 = "Stevenson D. S. Under a Crimson Sun: Prospects for Life in a Red Dwarf System. Springer, 2013."
        l2 = "все дальнейшие рассуждения, если без ссылок - с вики про возможность жизни на др планетах"
        l3 = "Waltham T., Bell F., Culshaw M. Sinkholes and Subsistence. Karst and Cavernous Rocks in Engineering and COnstruction"
        assert parse.is_source(l0)
        assert parse.is_source(l1)
        assert not parse.is_source(l2)
        assert parse.is_source(l3)

    @allure.story('Parsing pages')
    @allure.severity('blocker')
    def test_page(self):
        s0 = "стр. 0"
        s1 = "1"
        s2 = "asdf"
        s3 = "pp.100-101"
        assert parse.is_page(s0)
        assert parse.is_page(s1)
        assert not parse.is_page(s2)
        assert parse.is_page(s3)
