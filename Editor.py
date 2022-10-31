from Text import *


def log(message, color=None):
    logField = Editor.logField
    start = len(logField.text)
    logField.insert_text(len(logField.text), " " + str(message) + "\n")
    if len(logField.text) > 1000:
        logField.delete_text(0, len(logField.text) - 1000)
    Editor.logLayout.view_y = -Editor.logLayout.content_height
    if color is not None:
        logField.set_style(start, len(logField.text), attributes={"color": color})
    logField.insert_text(len(logField.text), " ")
    logField.set_style(len(logField.text) - 1, len(logField.text), attributes={"color": (255, 255, 255, 255)})


def generateConsole(window, command):
    windowSize = window.get_size()
    batch = Screen.renderGroups["console"]["batch"]
    back = Screen.renderGroups["console"]["groups"]["-1"]
    front = Screen.renderGroups["console"]["groups"]["0"]

    createRectangle(Vector2(8, windowSize[1] - 6), Vector2(100, windowSize[1] - 24), (0, 0, 0), batch, back)

    Editor.fpsDisplay = pyglet.text.Label("0", "Source Code Pro", 10, True, batch=batch, group=front)
    Editor.fpsDisplay.position = 12, windowSize[1] - 20

    createRectangle(Vector2(8, 272), Vector2(100, 248), (0, 0, 0), batch, back)

    titleField = Document("Console: ", Editor.logSettings)
    titleLayout = pyglet.text.layout.TextLayout(titleField, windowSize[0] - 22, 20, batch=batch, group=front)
    titleLayout.position = 12, 250

    createLines(Vector2(8, 272), Vector2(100, 248), (255, 255, 255), batch, back)
    createRectangle(Vector2(8, 242), Vector2(408, 38), (0, 0, 0), batch, back)

    logField = Document(" ", Editor.logSettings)
    logField.delete_text(0, 1)
    logLayout = Layout(logField, windowSize[0] - 22, 200, multiline=True, batch=batch, group=front)
    logLayout.position = 12, 40

    createRectangle(Vector2(8, 32), Vector2(windowSize[0] - 10, 8), (0, 0, 0), batch, back)

    commandField = Document(" ", Editor.commandSettings, command=command)
    commandLayout = Layout(commandField, windowSize[0] - 22, 20, batch=batch, group=front)
    commandLayout.position = 12, 10
    caret = Caret(commandLayout, color=(255, 255, 255), batch=batch)

    createLines(Vector2(8, 32), Vector2(windowSize[0] - 10, 8), (255, 255, 255), batch, back)

    Editor.commandField = commandField
    Editor.logField = logField
    Editor.logLayout = logLayout


def updateEditor(fps):
    pass


def updateWidgets(fps, normals=False):
    widgetShapes = []
    batch = Screen.renderGroups["widgets"]["batch"]

    for collider in Physics.colliders:
        transform = collider.gameObject.transform
        for p in range(len(collider.points)):
            p1, p2 = collider.points[p - 1], collider.points[p]
            p1, p2 = transform.localToScreen(p1), transform.localToScreen(p2)
            widgetShapes.append(pyglet.shapes.Line(p1.x, p1.y, p2.x, p2.y, color=(75, 255, 75), batch=batch))

            if normals:
                p3 = (p1 + p2) / 2
                p4 = p3 + (collider.normals[p-1] * Screen.unit / 10)
                widgetShapes.append(pyglet.shapes.Line(p3.x, p3.y, p4.x, p4.y, color=(255, 75, 75), batch=batch))

        p5 = transform.localToScreen(collider.com)
        widgetShapes.append(pyglet.shapes.Circle(p5.x, p5.y, 1, color=(255, 255, 255), batch=batch))

    Editor.widgetShapes = widgetShapes


def createLines(p1, p2, color, batch, group):
    lines = p1, Vector2(p2.x, p1.y), p2, Vector2(p1.x, p2.y)
    for i in range(len(lines)):
        d1, d2 = lines[i], lines[(i + 1) % len(lines)]
        Editor.consoleShapes.append(pyglet.shapes.Line(d1.x, d1.y, d2.x, d2.y, color=color, batch=batch,
                                                       group=group))


def createRectangle(p1, p2, color, batch, group):
    Editor.consoleShapes.append(pyglet.shapes.Rectangle(p1.x, p1.y, p2.x - p1.x, p2.y - p1.y, color, batch=batch,
                                                        group=group))
