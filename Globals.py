import pyglet.gl

from Imports import *
import json


def log(message):
    Editor.log += str(message) + "\n"


class Screen:
    unit = 64
    size = Vector2(0, 0)

    camera = None
    canvas = None

    sprites = []

    layers = ["default", "widgets", "console"]
    batches = [pyglet.graphics.Batch() for _ in range(3)]

    groups = {"0": pyglet.graphics.Group(order=0),
              "-1": pyglet.graphics.Group(order=-1)}

    widgets = []
    active_widget = None

    buffers = pyglet.image.get_buffer_manager()

    @staticmethod
    def add_layer(name, order):
        Screen.layers.insert(order, name)
        Screen.batches.insert(order, pyglet.graphics.Batch())
        Editor.toggle(name)

    @staticmethod
    def get_render_set(name, order, parent=None):
        order = str(int(order))
        if name in Screen.layers:
            num = Screen.layers.index(name)
        else:
            num = Screen.layers.index("default")
        layer = Screen.batches[num]
        if order in Screen.groups:
            group = Screen.groups[order]
        else:
            Screen.groups[order] = group = pyglet.graphics.Group(order=int(order))
        group.parent = parent if parent is not None else group.parent
        return layer, group

    @staticmethod
    def activate_widget(widget):
        if Screen.active_widget is not None:
            Screen.active_widget.caret.visible = False
            Screen.active_widget.caret.mark = Screen.active_widget.caret.position = 0
        if widget:
            widget.caret.visible = True
            widget.caret.mark = len(widget.document.text)
            widget.caret.position = len(widget.document.text)
            if widget.is_hint:
                widget.document.text = " "
                widget.document.set_style(0, 1, widget.style)
                widget.document.delete_text(0, 1)
                widget.is_hint = False
        Screen.active_widget = widget


class Editor:
    flags = ["play", "default"]
    log = ""

    constantCommands = []

    logField = None
    logLayout = None
    commandField = None

    previousCommands = []
    commandNum = 0

    logSettings = dict(font_name='Calibri', font_size=12,
                       color=(255, 255, 255, 255), background_color=(0, 0, 0, 255))
    commandSettings = dict(font_name='Calibri', font_size=12,
                           color=(255, 255, 255, 255), background_color=(0, 0, 0, 0))

    debugShapes = []
    consoleShapes = []

    @staticmethod
    def toggle(name):
        if name in Editor.flags:
            Editor.flags.remove(name)
        else:
            Editor.flags.append(name)


class Resources:
    gameObjects = []
    resourcePath = ""
    cameras = []

    keep = []

    sceneName = ""


class Physics:
    colliders = []
    timeScale = 1
    colliderTypes = []


class Game:
    settings = {}

    @staticmethod
    def loadSettings():
        file = open(Resources.resourcePath + "settings.txt")
        Game.settings = json.load(file)

    @staticmethod
    def saveSettings():
        file = open(Resources.resourcePath + "settings.txt", "w")
        json.dump(Game.settings, file, indent=4)


