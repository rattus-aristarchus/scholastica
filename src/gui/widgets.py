#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 27 13:44:51 2022

@author: kryis
"""

import os

from kivy.logger import Logger
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelHeader
from kivy.uix.textinput import TextInput
from kivy.properties import ObjectProperty

from util import CONF, STRINGS

LANG = CONF["misc"]["language"]


class View(BoxLayout):

    options = ObjectProperty()

    def __init__(self, controller, **kwargs):
        self.controller = controller
        super().__init__(**kwargs)
        self.options = Options()
        self.options.controller = self.controller
        self.tutorial = self.ids['tutorial'].__self__
        self.hint = self.ids['hint'].__self__
        self.sources = self.ids['sources'].__self__

        if not CONF['misc']['show_tutorial']:
            self.hide_tutorial()

        self.hint_shown = True

    def show_tutorial(self):
        self.ids['tutorial_parent'].add_widget(self.tutorial)
        self.options.ids['tutorial'].text = STRINGS['menu'][4][LANG]

    def hide_tutorial(self):
        self.ids['tutorial_parent'].remove_widget(self.tutorial)
        self.options.ids['tutorial'].text = STRINGS['menu'][5][LANG]

    def hide_hint(self):
        self.ids['tree_and_hint'].remove_widget(self.ids['hint'])
        self.hint_shown = False

    def show_hint(self):
        if not self.hint_shown:
            self.ids['tree_and_hint'].add_widget(self.hint, 1)
            self.hint_shown = True

# TODO: cancel button


class Sources(TabbedPanel):

    controller = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class SourceTab(TabbedPanelHeader):

    def __init__(self, source_file, controller, **kwargs):
        super().__init__(**kwargs)
        self._saved = True
        self.source_file = source_file
        self.content.ids['input'].controller = controller

        self.set_saved()
        self.load_text()

    def set_saved(self):
        self._saved = True
        self.text = os.path.basename(self.source_file.address)

    def set_unsaved(self):
        self._saved = False
        self.text = os.path.basename(self.source_file.address) + "**"

    def is_saved(self):
        return self._saved

    def load_text(self):
        self.content.ids['input'].text = self.source_file.text


class SourceTabContent(BoxLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ids['input'].bind(text=self.on_text)

    def on_text(self, text_input, text):
        pass


class SourceText(TextInput):

    controller = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        super().keyboard_on_key_down(window, keycode, text, modifiers)

        key = keycode[1]
        ctrl = 'ctrl' in modifiers

        if key == 'w' and ctrl:
            self.controller.close_current_tab()
        elif text == 'ц' and ctrl:
            self.controller.close_current_tab()

"""
the function through which passes any text added to the widget
    def insert_text(self, substring, from_undo=False): 
"""


class BasePopup(Popup):    
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.callback = None
    
    def enter(self):
        self.ok()
    
    def escape(self):
        self.dismiss()
        
    def ok(self):
        if self.callback is not None:
            self.callback()
        self.dismiss()


class FilePopup(Popup):
    
    def __init__(self, controller, **kwargs):
        super().__init__(**kwargs)
        self.controller = controller
        
        # I have found no simple way to change the text of labels inside the
        # file picker into different
        # languages; the following monstrosity takes care of that
        # Thankfully, it's not needed if the view is in icons instead of a list
        """
        for child in self.ids['filechooser'].children[0].children[0].children:
            if isinstance(child, BoxLayout):
                for child_1 in child.children:
                    if isinstance(child_1, Label) and child_1.text == "Name":
                        child_1.text = STRINGS["filechooser"][5][LANG]
                    if isinstance(child_1, Label) and child_1.text == "Size":
                        child_1.text = STRINGS["filechooser"][6][LANG]
                    """
      
    def close(self):
        self.dismiss()

    def set_path(self, path):
        self.ids["filechooser"].path = path


class OpenFile(FilePopup):
        
    def act(self, filechooser_selection, filename):
        self.dismiss()
        if self.controller is not None:
            if os.path.isdir(filechooser_selection):
                dir_path = filechooser_selection
            else:
                dir_path = os.path.dirname(filechooser_selection)
            path = os.path.join(dir_path, filename)
            self.controller.open_file(path)


class NewFile(FilePopup):
        
    def act(self, filechooser_selection, filename):
        self.dismiss()
        if self.controller is not None:
            if os.path.isdir(filechooser_selection):
                dir_path = filechooser_selection
            else:
                dir_path = os.path.dirname(filechooser_selection)
            path = os.path.join(dir_path, filename)
            self.controller.new_file(path)


class Tutorial(BoxLayout):

    controller = ObjectProperty()


class Options(DropDown):

    controller = ObjectProperty()

    def tutorial_text(self):
        if CONF['misc']['show_tutorial']:
            return STRINGS['menu'][4][LANG]
        else:
            return STRINGS['menu'][5][LANG]


class MenuButton(Button):

    pass
