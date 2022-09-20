import os
from kivy.logger import Logger

import util
from storage.sourcefile import SourceFile
import storage.tagfile as tagfile
from gui.widgets import SourceTab
from util import STRINGS, CONF

LANG = CONF['misc']['language']


class SourcesController:

    def __init__(self, main_controller):
        self.main_controller = main_controller
        self.tabs = []

    def set_view(self, view):
        self.view = view

    @property
    def sources(self):
        return self.view.ids['sources']

    def restore_session(self):
        for path in CONF['misc']['last_sources']:
            self.open_file(path, new=False)

    def open_file(self, path, new=True):
        # load the file
        file = self._create_source_file(path)
        if file is None:
            return
        self.update_source_file(file)
        if new:
            CONF['misc']['last_sources'].append(file.address)
            util.set_conf('misc', 'last_sources', CONF['misc']['last_sources'])
            util.set_conf('misc', 'default_location', os.path.dirname(path))

        # now, the tab
        new_tab = SourceTab(file, self)
        self.sources.add_widget(new_tab)
        self.sources.switch_to(new_tab, do_scroll=True)
        self.tabs.append(new_tab)

    def close_tab(self, tab):
        # first, finish with the file
        if isinstance(tab, SourceTab) and (tab.source_file.address in CONF['misc']['last_sources']):
            CONF['misc']['last_sources'].remove(tab.source_file.address)
            util.set_conf('misc', 'last_sources', CONF['misc']['last_sources'])

        # now, the tab
        self.tabs.remove(tab)
        self.sources.remove_widget(tab.content)
        self.sources.remove_widget(tab)
        if len(self.tabs) > 0:
            self.sources.switch_to(self.tabs[-1], do_scroll=True)

    def close_current_tab(self):
        self.close_tab(self.sources.current_tab)

    def save_files(self):
        #go through files that are mark unsaved, call update file, then mark saved
        for tab in self.tabs:
            tab.source_file.write(tab.get_text())
            self.mark_saved(tab)

    def _create_source_file(self, path):
        new_file = None
        try:
            tag_file = self.main_controller.tag_file
            new_file = SourceFile(path)
            new_file.read_sources(tag_file)
            new_file.read(tag_file)
        except FileNotFoundError as e:
            Logger.error(e.strerror + ": " + e.filename)
            message = STRINGS["error"][0][LANG][0] + \
                      e.filename + \
                      STRINGS["error"][0][LANG][1]
            self.main_controller.popup(message)
        return new_file

    def text_changed(self, tab):
        if isinstance(tab, SourceTab) and tab.is_saved():
            self.mark_unsaved(tab)

    def mark_unsaved(self, tab):
        if isinstance(tab, SourceTab):
            tab.set_unsaved()

    def mark_saved(self, tab):
        if isinstance(tab, SourceTab):
            tab.set_saved()

    def update_source_file(self, source_file):
        Logger.info(f"SourcesController: updating source file {source_file.address}")

        tag_file = self.main_controller.tag_file
        if tag_file is None:
            return

        source_file.read_sources(tag_file)
        source_file.read(tag_file)

        # First, we check if the file is one of those already tracked by the
        # application. If it is, all its content is reloaded.
        existing_file = None
        for check in tag_file.source_files:
            if check.address == source_file.address:
                existing_file = check
                break

        if existing_file is not None:
            # If it is already tracked:
            self._replace_existing(existing_file, source_file)
        else:
            # If it isn't, we read the file and see if it has any tags at all.
            # If it doesn't, there is no point in adding it
            if len(source_file.tags) > 0:
                self._add_source_file(source_file)
        return

    def _replace_existing(self, old_file, new_file):
        Logger.info("Messenger: file already exists. Removing old file.")

        self.view.ids['tree'].remove_all_from(old_file)
        self.main_controller.tag_file.remove_file(old_file)
        self._add_source_file(new_file)

    def _add_source_file(self, source_file):
        self.view.ids['tree'].add_all_from(source_file)
        self.main_controller.tag_file.add_file(source_file)
        tagfile.write_tag_file(self.main_controller.tag_file)
