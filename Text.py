from Globals import *


class Document(pyglet.text.document.FormattedDocument):
    def __init__(self, text, style, command=None):
        super().__init__(text)
        self.set_style(0, len(self.text), style)
        self.command = command
        self.layout = None
        Screen.documents.append(self)

    def on_insert_text(self, pos, text):
        if hasattr(self, "layout"):
            if self.layout is not None:
                if not self.layout.typing:
                    self.delete_text(pos, pos + 1)
                else:
                    if hasattr(self, "command"):
                        if self.command is not None:
                            if text == "\n":
                                self.delete_text(pos, pos + 1)
                                self.command(self.text)
                                self.text = ""


class Layout(pyglet.text.layout.IncrementalTextLayout):
    def __init__(self, doc, width, height, multiline=False, batch=None, group=None):
        super().__init__(doc, width, height, multiline=multiline, batch=batch, group=group)
        self.caret = None
        self.doc = doc
        doc.layout = self
        self.typing = False

    def setFocus(self, focus=True):
        if self.caret is not None:
            self.caret.visible = focus
        self.typing = focus

    def inLayout(self, x, y):
        return 0 < x - self.x < self.width and 0 < y - self.y < self.height


class Caret(pyglet.text.caret.Caret):
    def __init__(self, layout, color, batch):
        super().__init__(layout, color=color, batch=batch)
        layout.caret = self

        Screen.canvas.push_handlers(self)

    def on_mouse_press(self, x, y, button, modifiers):
        super().on_mouse_press(x, y, button, modifiers)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        pass


class TextField(Document):
    def __init__(self, text, style, width, height, command=None, multiLine=False, batch=None, textColor=None,
                 position=None):
        super().__init__(text, style, command)
        self.layout = Layout(self, width, height, multiline=multiLine, batch=batch)
        self.caret = Caret(self.layout, textColor, batch=batch)
        self.position = position if position is not None else Vector2(0, 0)
        self.layout.position = self.position.x, self.position.y

    def setPosition(self, position):
        self.position = position
        self.layout.position = position.x, position.y
