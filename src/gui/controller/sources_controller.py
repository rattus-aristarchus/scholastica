import os
from kivy.logger import Logger

from storage.sourcefile import SourceFile
import storage.tagfile as tagfile
from gui.widgets import SourceTab
from util import STRINGS, CONF

LANG = CONF['misc']['language']


class SourcesController:

    def __init__(self, main_controller):
        self.main_controller = main_controller
        # a dictionary with the tabs and corresponding source files
        self.tabs = []

    def set_view(self, view):
        self.view = view

    @property
    def sources(self):
        return self.view.ids['sources']

    def open_file(self, path):
        #TODO: add the file to CONF[misc][last_sources]
        #TODO: add the  file to self.tabs

        # load the file
        file = self._create_source_file(path)
        if file is None:
            return
        self.update_source_file(file)

        # now, the tab
        new_tab = SourceTab(file)
        self.sources.add_widget(new_tab)
        self.sources.switch_to(new_tab, do_scroll=True)

    def close_file(self, path):
        #TODO remove from CONF[misc][last_sources]
        #TODO remove from self.tabs
        pass

    def save_files(self):
        #go through files that are mark unsaved, call update file, then mark saved
        pass

        source_file.read_sources(tag_file)
        source_file.read(tag_file)

    def _create_source_file(self, path):
        new_file = None
        try:
            tag_file = self.main_controller.tag_file
            new_file = SourceFile(path, tag_file.backup_location)
            new_file.read_sources(tag_file)
            new_file.read(tag_file)
        except FileNotFoundError as e:
            Logger.error(e.strerror + ": " + e.filename)
            message = STRINGS["error"][0][LANG][0] + \
                      e.filename + \
                      STRINGS["error"][0][LANG][1]
            self.main_controller.popup(message)
        return new_file

    def mark_unsaved(self):
        pass

    def mark_saved(self):
        pass

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
        self.tag_file.remove_file(old_file)
        self._add_source_file(new_file)

    def _add_source_file(self, source_file):
        self.view.ids['tree'].add_all_from(source_file)
        self.tag_file.add_file(source_file)
        tagfile.write_tag_file(self.main_controller.tag_file)
