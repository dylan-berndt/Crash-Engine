import pyglet.shapes

from ObjectManager import *
from ScreenManager import *
from Physics import *
from Editor import *

Resources.resourcePath = open("config.txt").readline()
sys.path.append(Resources.resourcePath)


def init(windowSize, title: str = "Crash Engine", vsync=0, rate=1.0/120):
    Window(windowSize, title, vsync, rate)
    pyglet.app.run()


class Window(pyglet.window.Window):
    def __init__(self, windowSize, title: str = "Crash Engine", vsync=0, rate=1.0/120):
        assert type(windowSize) in [tuple, list, Vector2]
        super().__init__(windowSize[0], windowSize[1], vsync=vsync)
        Screen.canvas = self
        Screen.canvas.set_caption(title)
        Screen.size = windowSize

        generateConsole(self, command)

        pyglet.clock.schedule_interval(update, rate)

    def on_mouse_press(self, x, y, button, modifiers):
        for document in Screen.documents:
            if document.layout is not None:
                if document.layout.caret is not None:
                    layout = document.layout
                    layout.setFocus(layout.inLayout(x, y))

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        for document in Screen.documents:
            if document.layout is not None:
                layout = document.layout
                if layout.inLayout(x, y):
                    layout.view_y += scroll_y * layout.dpi

    def on_draw(self):
        Screen.canvas.clear()
        for layer in Screen.renderGroups:
            if not (layer == "widget" and "widgets" not in Editor.flags):
                if not (layer == "console" and "console" not in Editor.flags):
                    Screen.renderGroups[layer]["batch"].draw()

    def on_key_press(self, symbol, modifiers):
        if symbol == key.UP and "console" in Editor.flags and Editor.previousCommands:
            Editor.commandNum = max(Editor.commandNum - 1, -len(Editor.previousCommands))
            Editor.commandField.text = Editor.previousCommands[Editor.commandNum]

        if symbol == key.DOWN and "console" in Editor.flags:
            Editor.commandNum = min(Editor.commandNum + 1, len(Editor.previousCommands) + 1)
            if Editor.commandNum == 0:
                Editor.commandField.text = ""
            else:
                Editor.commandField.text = Editor.previousCommands[Editor.commandNum]

        if symbol == key.SLASH and (modifiers & key.MOD_CTRL):
            Editor.toggle("console")
            Editor.commandField.layout.setFocus()

        if symbol == key.N and (modifiers & key.MOD_CTRL):
            Editor.toggle("normals")

        if symbol == key.W and (modifiers & key.MOD_CTRL):
            Editor.toggle("widgets")

        Input.keys.append(symbol)
        Input.modifiers = modifiers

    def on_key_release(self, symbol, modifiers):
        if symbol in Input.keys:
            Input.keys.remove(symbol)
        Input.modifiers = modifiers


def update(dt):
    fps = pyglet.clock.get_fps()
    Editor.fpsDisplay.text = str(round(fps * 100) / 100)

    for constant in Editor.constantCommands:
        try:
            exec(constant)
        except Exception as e:
            log("Constant command " + constant + " caused issue: \n" +
                str(e) + "\nTerminating command")
            Editor.constantCommands.remove(constant)

    if "play" in Editor.flags:
        for gameObject in Resources.gameObjects:
            gameObject.update(dt * Physics.timeScale)

    if "edit" in Editor.flags:
        updateEditor(fps)

    if "widgets" in Editor.flags:
        updateWidgets(fps, "normals" in Editor.flags)
    else:
        Editor.widgetShapes = []

    if "console" in Editor.flags:
        pass
    else:
        Editor.commandField.text = ""


def loadScene(filePath):
    while Resources.gameObjects:
        destroy(Resources.gameObjects[0])
    Editor.widgetShapes = []
    file = open(os.path.join(Resources.resourcePath, filePath + ".scene"))
    split = file.read().split("\n")
    for item in split:
        if "from Crash import *" in item:
            split.remove(item)
    read = "\n".join(split)
    program = compile(read, os.path.join(Resources.resourcePath, filePath + ".scene"), mode="exec")
    exec(program)


def command(text):
    if "console" in Editor.flags:
        for line in text.split("(+)"):
            if line.strip():
                plainText = line.strip()
                Editor.previousCommands.append(plainText)
                if plainText.startswith("#add-command"):
                    plainText = plainText.lstrip("#add-command")
                    plainText = plainText.strip()
                    try:
                        exec(plainText)
                        Editor.constantCommands.append(plainText)
                        log("Constant command added: " + plainText)
                    except Exception as e:
                        log("Error: ", color=(255, 50, 50, 255))
                        log(str(e))
                elif plainText.startswith("#remove-command"):
                    plainText = plainText.lstrip("#remove-command")
                    plainText = plainText.strip()
                    try:
                        commandName = Editor.constantCommands.pop(int(plainText))
                        log("Removed constant command: " + commandName)
                    except Exception as e:
                        log("Error: ", color=(255, 50, 50, 255))
                        log(str(e))
                elif plainText.startswith("#rc"):
                    if len(Editor.constantCommands) > 0:
                        commandName = Editor.constantCommands.pop()
                        log("Removed constant command: " + commandName)
                else:
                    try:
                        log("Command: " + plainText)
                        exec(plainText)
                    except Exception as e:
                        log("Error: ", color=(255, 50, 50, 255))
                        log(str(e))
