import glob

import pyglet.sprite
import pyperclip
from Globals import *
from ObjectManager import Transform


class Scroll(Component):
    def __init__(self, group, dpi=96, upper_bound=None, lower_bound=None):
        self.gameObject = None

        self.group = group
        self.items = []

        self.dpi = dpi

        self.lower_bound = lower_bound if lower_bound is not None else Vector2(0, 0)
        self.upper_bound = upper_bound if upper_bound is not None else Vector2(0, 0)

        self.on_mouse_scroll(self.group.position.x + 1, self.group.position.y + 1, 0, 0)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        pos = Transform.worldToScreen(self.group.position)
        size = self.group.size * Screen.unit
        g_x, g_y, width, height = pos.x, pos.y, size.x, size.y
        if g_x - width // 2 < x < g_x + width // 2:
            if g_y - height // 2 < y < g_y + height // 2:
                x, y = self.group.view_x + scroll_x * self.dpi, self.group.view_y + scroll_y * self.dpi
                self.group.view_x = max(min(x, self.upper_bound.x), self.lower_bound.x)
                self.group.view_y = max(min(y, self.upper_bound.y), self.lower_bound.y)

    def destroy(self):
        self.group.clear()


class ScissorGroup(pyglet.graphics.Group):
    def __init__(self, position, size, parent=None, order=0):
        self.position = position
        self.size = size

        self.view_x = 0
        self.view_y = 0

        self.was_scissor_enabled = False

        super().__init__(parent=parent, order=order)

    def clear(self):
        self.visible = False

    def set_state(self):
        self.was_scissor_enabled = gl.glIsEnabled(gl.GL_SCISSOR_TEST)
        gl.glEnable(gl.GL_SCISSOR_TEST)

        # gl.glTranslatef(-self.view_x, -self.view_y, 0)

        size = self.size * Screen.unit
        width, height = size.x, size.y

        pos = Transform.worldToScreen(self.position)
        x, y = pos.x, pos.y

        gl.glScissor(int(x - width // 2), int(y - height // 2),
                     int(width), int(height))

    def unset_state(self):
        # gl.glTranslatef(self.view_x, self.view_y, 0)

        if not self.was_scissor_enabled:
            gl.glDisable(gl.GL_SCISSOR_TEST)


class Button(Component):
    def __init__(self, size, function, args=None):
        self.gameObject = None

        self.size = size
        self.function = function
        self.args = args

    def __deepcopy__(self, memo):
        return Button(self.size, self.function, self.args)

    def update(self, fpsDelta):
        pass

    def on_mouse_click(self, x, y, button, modifiers):
        if self.gameObject is not None and button & pyglet.window.mouse.LEFT:
            transform = self.gameObject.transform
            pos = transform.worldToScreen(transform.position)
            size = self.size * Screen.unit
            if pos.x - size.x // 2 < x < pos.x + size.x // 2:
                if pos.y - size.y // 2 < y < pos.y + size.y // 2:
                    if self.args is not None:
                        self.function(self.args)
                    else:
                        self.function()


class TextWidget(Component):
    def __init__(self, text, style, width, batch=None,
                 group=Screen.groups["0"], position=None, editable=False,
                 multiline=False, height=None, command=None, hint="",
                 hint_color=None):
        batch = batch if batch is not None else Screen.batches[Screen.layers.index("default")]
        self.gameObject = None
        self.position = position if position is not None else Vector2(0, 0)

        flag = len(text) == 0
        if len(text) == 0:
            text = " "
        self.document = pyglet.text.document.FormattedDocument(text)
        self.document.set_style(0, len(self.document.text), style)
        self.style = style
        if flag:
            self.document.delete_text(0, 1)

        self.hint = hint
        self.hint_color = hint_color if hint_color is not None else [175, 175, 190, 255]
        self.is_hint = False

        font = self.document.get_font(0)
        height = font.ascent - font.descent if height is None else height

        self.layout = pyglet.text.layout.IncrementalTextLayout(
            self.document, width, height, multiline=multiline, batch=batch, group=group)

        self.layout.x = self.position.x
        self.layout.y = self.position.y

        self.width = width
        self.height = height
        self.size = Vector2(self.width, self.height)

        color = style["color"][:3]
        self.caret = pyglet.text.caret.Caret(self.layout, color=color, batch=batch) if editable else None

        self.editable = editable
        self.command = command

        self.batch = batch
        self.group = group

        Screen.widgets.append(self)

    def destroy(self):
        if Screen.active_widget == self:
            Screen.activate_widget(None)
        self.layout.delete()
        Screen.widgets.remove(self)

    def update(self, fpsDelta):
        transform = self.gameObject.transform
        self.position = transform.worldToScreen(transform.position) - self.size // 2

        self.layout.x, self.layout.y = int(self.position.x), int(self.position.y)

        if len(self.document.text) < 1:
            if Screen.active_widget != self and not self.is_hint:
                edit_style = copy.copy(self.style)
                edit_style["color"] = self.hint_color
                self.document.insert_text(0, self.hint, edit_style)
                self.is_hint = True
            return
        self.document.set_style(1, len(self.document.text), dict(indent=-16))

    def hit_test(self, mx, my):
        if self.position.x < mx < self.position.x + self.layout.width:
            if self.position.y < my < self.position.y + self.layout.height:
                return True
        return False

