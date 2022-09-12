import os

from gui.widgets import SourceTab


class SourcesController:

    def __init__(self, main_controller):
        self.main_controller = main_controller
        # a dictionary with the tabs and corresponding source files
        self.tabs = {}

    def set_view(self, view):
        self.view = view

    @property
    def sources(self):
        return self.view.ids['sources']

    def open_file(self, path):
        #TODO: add the  file to self.tabs
        name = os.path.basename(path)
        new_tab = SourceTab(name)
        self.sources.add_widget(new_tab)
        self.sources.switch_to(new_tab, do_scroll=True)

    def save_files(self):
        pass
