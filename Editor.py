from UI import *


def log(*args, color=None):
    for message in args:
        logField = Editor.logField.document
        start = len(logField.text)
        logField.insert_text(len(logField.text), " " + str(message) + "\n")
        Editor.logLayout.view_y = -Editor.logLayout.content_height
        if color is not None:
            logField.set_style(start, len(logField.text), attributes={"color": color})
        logField.insert_text(len(logField.text), " ")
        logField.set_style(len(logField.text) - 1, len(logField.text), attributes={"color": (255, 255, 255, 255)})


def generateConsole(window, command):
    windowSize = window.get_size()
    batch = Screen.batches[Screen.layers.index("console")]
    back = Screen.groups["-1"]
    front = Screen.groups["0"]

    field(Vector2(8, 384), Vector2(100, 354), batch, back)

    titleField = TextWidget(" Console: ", Editor.logSettings, windowSize[0] - 22, batch=batch, group=front,
                            position=Vector2(12, 361))

    field(Vector2(8, 348), Vector2(windowSize[0] - 10, 44), batch, back)

    logField = TextWidget(" ", Editor.logSettings, windowSize[0] - 22, multiline=True, batch=batch,
                          group=front, position=Vector2(12, 48), height=296)

    field(Vector2(8, 40), Vector2(windowSize[0] - 10, 8), batch, back)

    commandField = TextWidget(" ", Editor.commandSettings, windowSize[0] - 22, command=command, batch=batch,
                              group=front, position=Vector2(12, 15), editable=True)

    Editor.commandField = commandField
    Editor.logField = logField
    Editor.logLayout = logField.layout


def updateEditor(fps):
    pass


def updateWidgets(fps, normals=False):
    widgetShapes = []
    batch = Screen.layers["widgets"]

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

    for gameObject in Resources.gameObjects:
        for component in gameObject.components:
            if isinstance(component, Button):
                p = gameObject.transform.worldToScreen(gameObject.transform.position)
                s = component.size * Screen.unit
                p1 = p - s // 2
                p2 = p + s // 2
                lines = p1, Vector2(p2.x, p1.y), p2, Vector2(p1.x, p2.y)
                for i in range(len(lines)):
                    d1, d2 = lines[i], lines[(i + 1) % len(lines)]
                    widgetShapes.append(pyglet.shapes.Line(d1.x, d1.y, d2.x, d2.y,
                                                           color=(0, 255, 0), batch=batch,))

    Editor.debugShapes = widgetShapes


def field(p1, p2, batch, group):
    lines = p1, Vector2(p2.x, p1.y), p2, Vector2(p1.x, p2.y)
    for i in range(len(lines)):
        d1, d2 = lines[i], lines[(i + 1) % len(lines)]
        Editor.consoleShapes.append(pyglet.shapes.Line(d1.x, d1.y, d2.x, d2.y, color=(255, 255, 255), batch=batch,
                                                       group=group))
    # i have no idea why i have to do this +1 -1 horseshit in the directions that i have to but im gonna kablooey
    Editor.consoleShapes.append(pyglet.shapes.Rectangle(p1.x, p1.y - 1, p2.x - p1.x - 1, p2.y - p1.y + 1, (0, 0, 0),
                                                        batch=batch, group=group))

