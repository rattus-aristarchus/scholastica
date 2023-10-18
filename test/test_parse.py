#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 27 18:34:31 2022

@author: kryis
"""

import pytest
import storage.parse as parse
from data.base_types import Tag
from data.tag_nest import TagNest


@pytest.fixture
def tag_nest():
    return TagNest()


def test_tag_parser(tag_nest):
    tag_line_0 = " (first_tag, second_tag) \n"
    tag_line_1 = "     (;afkaj;fdjasdfl1342-`-0)\n"
    not_tag_line_0 = "asdl;kfjasjlkf;akwe\n"
    assert parse.is_enclosed(tag_line_0)
    first_tag = Tag("first_tag")
    nest = tag_nest
    nest.tags = [first_tag]
    assert parse.get_tags(tag_line_0, nest, False)[0] == first_tag
    assert parse.is_enclosed(tag_line_1)
    assert not parse.is_enclosed(not_tag_line_0)
    print("check_tag_parser - done")


def test_source():
    lines = ["Levin, S. A. (ed.), Princeton guide to ecology. Princeton Univ. Press. Part VII Managing the Biosphere",
             "Stevenson D. S. Under a Crimson Sun: Prospects for Life in a Red Dwarf System. Springer, 2013.",
             "Waltham T., Bell F., Culshaw M. Sinkholes and Subsistence. Karst and Cavernous Rocks in Engineering and COnstruction",
             "https://www.testim.io/blog/qa-metrics-an-introduction/"]
    not_lines = ["все дальнейшие рассуждения, если без ссылок - с вики про возможность жизни на др планетах"]
    for line in lines:
        assert parse.is_source(line)
    for line in not_lines:
        assert not parse.is_source(line)
    print("check_source - done")


def test_page():
    s0 = "стр. 0"
    s1 = "1"
    s2 = "asdf"
    s3 = "pp.100-101"
    assert parse.is_page(s0)
    assert parse.is_page(s1)
    assert not parse.is_page(s2)
    assert parse.is_page(s3)
    print("check_page - done")
