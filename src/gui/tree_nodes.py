from kivy.logger import Logger
from kivy.uix.gridlayout import GridLayout
from kivy.uix.treeview import TreeViewNode

from util import CONF


class EntNode(GridLayout, TreeViewNode):

    def __init__(self, entity, **kwargs):
        super().__init__(**kwargs)
        if entity is None:
            Logger.warning("creating node with None entity")
        self.entity = entity
        self.load_text()

    def load_text(self):
        self.ids['label'].text = self.entity.text
        self.set_text_height()

    def set_text_height(self):
        if self.entity.text == "":
            self.height = 17
        else:
            self.height = self.minimum_height

    def copy(self):
        return EntNode(self.entity)


class SourceNode(EntNode):

    def __init__(self, source, file, **kwargs):
        super().__init__(source, **kwargs)
        self.file = file

    def load_text(self):
        self.ids['label'].text = "[i]" + self.entity.text + "[/i]"
        self.set_text_height()


class EntryNode(EntNode):

    def __init__(self, entry, file, **kwargs):
        self.full_text = False
        super().__init__(entry, **kwargs)
        self.file = file

        if entry.source is not None:
            reference = "(" + entry.source.get_first_word()
            if len(entry.page) > 0:
                reference += ", " + entry.page
            reference += ")"
            self.ids['reference'].text = reference
        else:
            self.remove_widget(self.ids['reference'])

        if not len(entry.comments) == 0:
            comments = ""
            for comment in entry.comments:
                comments += "//" + comment + "\n"
            self.ids['comment'].text = comments[:-1]
        else:
            self.remove_widget(self.ids['comment'])

    def load_text(self):
        if self.full_text:
            self.ids['label'].text = self.no_last_n()
        elif len(self.entity.text) < CONF["text"]["snippet_length"]:
            self.ids['label'].text = self.no_last_n()
        else:
            self.ids['label'].text = \
                self.entity.text[:CONF["text"]["snippet_length"]] + " ..."

        self.set_text_height()

    def no_last_n(self):
        text = self.entity.text
        #   Logger.debug("EntryNode: last two symbols of text are " + text[-2] + " and " + text[-1])
        if len(text) > 0 and text[-1:] == "\n":
            Logger.debug("EntryNode: removing last \\n")
            return text[:-1]
        else:
            Logger.debug(f"EntryNode: displaying text {self.entity.text}")
            return text


class TagNode(EntNode):

    def __init__(self, tag, controller, main_controller, **kwargs):
        super().__init__(tag, **kwargs)
        self.controller = controller
        self.main_controller = main_controller
        self.input = self.ids['input'].__self__
        self.label = self.ids['label'].__self__
        self.remove_widget(self.input)
        self.editing = False

        # The tree is only loaded up to a certain depth;
        # upon reaching the load point, the next n nodes are loaded
        self.load_point = False

    def copy(self):
        return TagNode(self.entity, self.controller, self.main_controller)

    """
    Methods that change the appearance of the node
    """

    def edit_done(self):
        self.save_text()
        self.label_mode()
        self.load_text()

    def label_mode(self):
        if self.editing:
            self.remove_widget(self.input)
            self.input.focus = False
            self.add_widget(self.label)
            self.editing = False
            self.main_controller.return_kbd()

    def input_mode(self):
        if not self.editing:
            self.remove_widget(self.label)
            self.add_widget(self.input)
            self.input.focus = True
            self.editing = True

    def cursor_to_end(self):
        if self.editing:
            self.input.cursor = (len(self.input.text), 0)

    def cursor_to_start(self):
        if self.editing:
            self.input.cursor = (0, 0)

    def select_text(self):
        if self.editing:
            self.input.select_all()

    """
    Methods that change the data based on user input
    """

    def save_text(self):
        text = self.ids['input'].text
        if text == "" or text.isspace():
            self.controller.delete_node(self)
        else:
            self.controller.edit_tag(self.entity, self.ids['input'].text)

    def edit_text(self):
        self.ids['input'].text = self.entity.text
