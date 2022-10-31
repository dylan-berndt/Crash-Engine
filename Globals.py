from Imports import *


def log(message):
    Editor.log += message + "\n"


class Screen:
    unit = 64
    size = Vector2(0, 0)

    camera = None
    canvas = None

    sprites = []

    renderGroups = {"default": {"batch": pyglet.graphics.Batch(), "groups": {"0": pyglet.graphics.OrderedGroup(0)}},
                    "widgets": {"batch": pyglet.graphics.Batch(), "groups": {"0": pyglet.graphics.OrderedGroup(0)}},
                    "console": {"batch": pyglet.graphics.Batch(), "groups": {"0": pyglet.graphics.OrderedGroup(0),
                                                                             "-1": pyglet.graphics.OrderedGroup(-1)}}}

    documents = []


class Editor:
    flags = ["play"]
    log = ""

    constantCommands = []

    fpsDisplay = None

    logField = None
    logLayout = None
    commandField = None

    previousCommands = []
    commandNum = 0

    logSettings = dict(font_name='Source Code Pro', font_size=10,
                       color=(255, 255, 255, 255), background_color=(0, 0, 0, 255))
    commandSettings = dict(font_name='Source Code Pro', font_size=10,
                           color=(255, 255, 255, 255), background_color=(0, 0, 0, 0))

    widgetShapes = []
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


class Input:
    keys = []
    modifiers = []
    justPressed = []


class Physics:
    colliders = []
    timeScale = 1
    colliderTypes = []
