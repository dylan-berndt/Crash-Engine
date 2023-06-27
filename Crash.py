from ObjectManager import *
from ScreenManager import *
from Physics import *
from Editor import *

Resources.resourcePath = open("config.txt").readline()
sys.path.append(Resources.resourcePath)


class Window(pyglet.window.Window):
    def __init__(self, windowSize, title: str = "Crash Engine", vsync=0, rate=1.0/120,
                 resizable=False, fullscreen=False, sceneName="Scenes/splash"):

        Game.loadSettings()

        assert type(windowSize) in [tuple, list, Vector2]
        super().__init__(windowSize[0], windowSize[1], vsync=vsync, resizable=resizable,
                         fullscreen=fullscreen)

        Screen.canvas = self
        Screen.canvas.set_caption(title)
        Screen.size = windowSize

        generateConsole(self, command)

        loadScene(sceneName)

        pyglet.clock.schedule_interval(update, rate)

        pyglet.app.run()

    def on_mouse_press(self, x, y, button, modifiers):
        for gameObject in Resources.gameObjects:
            gameObject.on_mouse_click(x, y, button, modifiers)

        widget_select = False
        for widget in Screen.widgets:
            if widget.hit_test(x, y) and widget.editable:
                widget_select = True
                Screen.activate_widget(widget)
                Screen.active_widget.caret.on_mouse_press(x, y, button, modifiers)
        if not widget_select:
            Screen.activate_widget(None)

    def on_mouse_release(self, x, y, button, modifiers):
        for gameObject in Resources.gameObjects:
            gameObject.on_mouse_release(x, y, button, modifiers)

    def on_mouse_motion(self, x, y, dx, dy):
        for gameObject in Resources.gameObjects:
            gameObject.on_mouse_motion(x, y, dx, dy)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        for gameObject in Resources.gameObjects:
            gameObject.on_mouse_drag(x, y, dx, dy, buttons, modifiers)
        if Screen.active_widget:
            Screen.active_widget.caret.on_mouse_drag(x, y, dx, dy, buttons, modifiers)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        for widget in Screen.widgets:
            if widget.hit_test(x, y):
                widget.layout.view_y += scroll_y * widget.layout.dpi

        for gameObject in Resources.gameObjects:
            gameObject.on_mouse_scroll(x, y, scroll_x, scroll_y)

    def on_draw(self):
        Screen.canvas.clear()
        for layer in Screen.layers:
            if not (layer == "widget" and "widgets" not in Editor.flags):
                if not (layer == "console" and "console" not in Editor.flags):
                    Screen.layers[layer].draw()
            if layer == "default":
                for canvas in GameObject.getEveryComponentOfType("Canvas"):
                    canvas.blit()

    def on_key_press(self, symbol, modifiers):
        if symbol == key.TAB:
            if Screen.active_widget:
                index = (Screen.widgets.index(Screen.active_widget) + 1) % len(Screen.widgets)
            else:
                index = 0

            j = 0
            while not Screen.widgets[index].editable and j < len(Screen.widgets):
                j += 1
                index = (index + 1) % len(Screen.widgets)
            if Screen.widgets[index].editable:
                Screen.activate_widget(Screen.widgets[index])
            else:
                Screen.activate_widget(None)

        if symbol == key.V and (modifiers & key.MOD_CTRL):
            self.on_text(pyperclip.paste())

        if symbol == key.C and (modifiers & key.MOD_CTRL):
            if Screen.active_widget is not None:
                widget = Screen.active_widget
                caret = widget.caret
                pyperclip.copy(widget.document.text[caret.position: caret.mark])

        if symbol == key.A and (modifiers & key.MOD_CTRL):
            if Screen.active_widget:
                caret = Screen.active_widget.caret
                caret.position, caret.mark = 0, len(Screen.active_widget.document.text)

        # if symbol == key.UP and "console" in Editor.flags and Editor.previousCommands:
        #     Editor.commandNum = max(Editor.commandNum - 1, -len(Editor.previousCommands))
        #     Editor.commandField.document.text = Editor.previousCommands[Editor.commandNum]
        #
        # if symbol == key.DOWN and "console" in Editor.flags:
        #     Editor.commandNum = min(Editor.commandNum + 1, len(Editor.previousCommands) + 1)
        #     if Editor.commandNum == 0:
        #         Editor.commandField.document.text = ""
        #     else:
        #         Editor.commandField.document.text = Editor.previousCommands[Editor.commandNum]

        if symbol == key.SLASH and (modifiers & key.MOD_CTRL):
            Editor.toggle("console")
            Screen.activate_widget(Editor.commandField)

        if symbol == key.N and (modifiers & key.MOD_CTRL):
            Editor.toggle("normals")

        if symbol == key.W and (modifiers & key.MOD_CTRL):
            Editor.toggle("widgets")

        for gameObject in Resources.gameObjects:
            gameObject.on_key_press(symbol, modifiers)

    def on_key_release(self, symbol, modifiers):
        for gameObject in Resources.gameObjects:
            gameObject.on_key_release(symbol, modifiers)

    def on_text(self, text):
        if Screen.active_widget:
            if "\r" in text:
                if Screen.active_widget.command:
                    try:
                        Screen.active_widget.command(Screen.active_widget.document.text)
                    except TypeError:
                        Screen.active_widget.command()
            else:
                Screen.active_widget.caret.on_text(text)

    def on_text_motion(self, motion):
        if Screen.active_widget:
            Screen.active_widget.caret.on_text_motion(motion)

    def on_text_motion_select(self, motion):
        if Screen.active_widget:
            Screen.active_widget.caret.on_text_motion_select(motion)

    def on_resize(self, width, height):
        super().on_resize(width, height)
        Screen.size = Vector2(width, height)


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
        for gameObject in Resources.gameObjects:
            gameObject.late_update(dt * Physics.timeScale)

    if "edit" in Editor.flags:
        updateEditor(fps)

    if "widgets" in Editor.flags:
        updateWidgets(fps, "normals" in Editor.flags)
    else:
        Editor.debugShapes = []

    if "console" in Editor.flags:
        pass
    else:
        Editor.commandField.document.text = ""


def loadScene(filePath):
    Screen.activate_widget(Editor.commandField)
    keep = []
    Resources.sceneName = filePath

    while Resources.gameObjects:
        if not hasattr(Resources.gameObjects[0], "keepOnLoad"):
            destroy(Resources.gameObjects[0])
        else:
            keep.append(Resources.gameObjects.pop(0))

    for gameObject in keep:
        Resources.gameObjects.append(gameObject)

    Editor.debugShapes = []
    file = open(os.path.join(Resources.resourcePath, filePath + ".scene"))
    split = file.read().split("\n")
    for item in split:
        if "from Crash import *" in item:
            split.remove(item)
    read = "\n".join(split)
    program = compile(read, os.path.join(Resources.resourcePath, filePath + ".scene"), mode="exec")
    exec(program)

    log("Loaded scene: (" + filePath + ")", color=(0, 255, 0, 255))


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
