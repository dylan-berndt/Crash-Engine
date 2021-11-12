from Globals import *
from ScreenManager import *
from PhysicsManager import *
from FileManager import *


def runTerminal(string):
    try:
        GameObject.Find("terminalInput").getComponent(TextField).text = ""
        exec(string)
    except Exception as e:
        print(e)

def log(string):
    Editor.terminalList.append(str(string))

def manageInput(events, mousePosition):
    Input.leftClick = False
    Input.rightClick = False
    Input.justPressed = []

    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                Input.leftClick = True

        if event.type == pygame.KEYDOWN:
            Input.keysDown.append(event.key)
            Input.unicodeDown.append(event.unicode)
            Input.justPressed.append(event.unicode)

            if event.key == pygame.K_BACKSLASH and pygame.key.get_mods() & pygame.KMOD_SHIFT:
                Editor.sceneView = not Editor.sceneView
                if not Editor.sceneView:
                    Editor.terminalActive = False

            if event.key == pygame.K_ESCAPE and Editor.sceneView:
                Editor.terminalActive = not Editor.terminalActive

            if event.key == pygame.K_TAB and Editor.terminalActive:
                log(" ")
                log("Current GameObjects: ")
                for gameObject in Resources.gameObjects:
                    log(gameObject.name + " | active: " + str(gameObject.active))

        if event.type == pygame.KEYUP:
            Input.keysDown.remove(event.key)
            Input.unicodeDown.remove(event.unicode)

        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
    Input.mousePosition = mousePosition

def updateEditor(fpsDelta):
    if Editor.sceneView:
        GameObject.Find("fpsDisplay").getComponent(Text).text = str(round(10/fpsDelta) / 10)

        rowHeight = (Canvas.defaultFont.get_height() + 4)

        for gameObject in Resources.gameObjects:
            pygame.draw.circle(Canvas.main, (255, 255, 255), toScreenPos(gameObject.transform.position).toList(), 2, 1)

            if gameObject != Canvas.mainCamera and not Editor.terminalActive:
                if Vector2.distance(Input.mousePosition, toScreenPos(gameObject.transform.position)) < 20:
                    textLines = []
                    textLines.append("GameObject: " + gameObject.name)
                    textLines.append("Position: " + str(round(gameObject.transform.position * 100) / 100))
                    textLines.append("Rotation: " + str(round(gameObject.transform.rotation)))
                    textLines.append("Local Position: " + str(round(gameObject.transform.localPosition * 100) / 100))
                    textLines.append("Components: ")
                    for component in gameObject.components:
                        textLines.append("      " + str(type(component).__name__))

                    boxHeight = len(textLines * rowHeight) + 10
                    boxWidth = max([Canvas.defaultFont.render(x, True, (255, 255, 255)).get_width() for x in textLines]) + 10

                    infoBox = pygame.Surface((boxWidth, boxHeight))

                    for t, text in enumerate(textLines):
                        infoBox.blit(Canvas.defaultFont.render(text, True, (255, 255, 255)), (5, 5 + (t * rowHeight)))

                    borderChange = Input.mousePosition - Vector2(0, boxHeight)
                    borderChange.x = max(min(borderChange.x, (Canvas.screenSize.x - (boxWidth + 10))), 10)
                    borderChange.y = max(min(borderChange.y, (Canvas.screenSize.y + (boxHeight - 10))), 10)
                    Canvas.main.blit(infoBox, borderChange.toList())

        if Editor.terminalActive:
            boxHeight = Canvas.screenSize.y
            totalHeight = rowHeight * len(Editor.terminalList)
            boxWidth = Canvas.screenSize.x
            mockTerminal = pygame.Surface((boxWidth, boxHeight))
            for t, text in enumerate(Editor.terminalList):
                mockTerminal.blit(Canvas.defaultFont.render(text, True, (255, 255, 255)),
                                  (5, ((t - 2) * rowHeight) + (boxHeight - totalHeight)))

            Canvas.main.blit(mockTerminal, (0, 0))

    else:
        GameObject.Find("fpsDisplay").getComponent(Text).text = ""

    terminalInput = GameObject.Find("terminalInput")
    terminalInput.active = Editor.terminalActive
    terminalInput.getComponent(TextField).focused = Editor.terminalActive
    GameObject.Find("fpsDisplay").update(fpsDelta)
    terminalInput.update(fpsDelta)


def update(fpsDelta):
    if Time.paused:
        fpsDelta = 0

    Time.time += fpsDelta
    Time.frame += 1

    Canvas.drawn = False

    for gameObject in Resources.gameObjects:
        if gameObject.active and gameObject.name != "terminalInput" and gameObject.name != "fpsDisplay":
            gameObject.update(fpsDelta)

    updateEditor(fpsDelta)

def addComponent(component):
    Resources.gameObjects[-1].addComponent(component)

def instantiate(gameObject, active=True):
    newObject = recreate(gameObject)
    newObject.active = active
    return newObject


class GameObject:
    def __init__(self, position=None, rotation=0, name=""):
        self.name = name
        self.transform = Transform(position if position is not None else Vector2(0, 0),
                                   rotation)
        self.components = [self.transform]
        self.active = True
        log("Created GameObject " + name + " at " + str(position))
        Resources.gameObjects.append(self)

    def update(self, fpsDelta):
        for component in self.components:
            component.update(fpsDelta)

    def addComponent(self, component):
        self.components.append(component)
        log("Added " + str(type(component).__name__) + " to " + self.name)
        component.gameObject = self

    def getComponent(self, componentType):
        for component in self.components:
            if type(component) == componentType:
                return component

    @staticmethod
    def Find(name):
        for gameObject in Resources.gameObjects:
            if gameObject.name == name:
                return gameObject

    @staticmethod
    def getAllWithComponent(componentType):
        objectList = []
        for gameObject in Resources.gameObjects:
            if gameObject.getComponent(componentType) is not None:
                objectList.append(gameObject)
        return objectList


class Transform:
    def __init__(self, position=None, rotation=0, localPosition=None, localRotation=0, rotationLocked=False):
        self.gameObject = None
        self.parent = None
        self.children = []

        self.position = position if position is not None else Vector2(0, 0)
        self.localPosition = localPosition if localPosition is not None else Vector2(0, 0)
        self.rotation = rotation
        self.localRotation = localRotation

        self.rotationLocked = rotationLocked

    def update(self, fpsDelta):
        if self.parent is not None:
            if not self.rotationLocked:
                rotationPosition = self.localPosition.rotate(self.parent.transform.rotation)
                self.rotation = self.localRotation + self.parent.transform.rotation
                self.position = self.parent.transform.position + rotationPosition
            else:
                self.position = self.parent.transform.position + self.localPosition
        self.rotation = self.rotation % 360

    def addChild(self, gameObject):
        self.children.append(gameObject)
        gameObject.transform.parent = self.gameObject
        gameObject.transform.localPosition = gameObject.transform.position

    def setParent(self, gameObject):
        self.parent = gameObject
        gameObject.transform.children.append(self.gameObject)
        self.localPosition = self.position

    def removeChild(self, gameObject):
        self.children.remove(gameObject)
        gameObject.transform.parent = None
        gameObject.transform.localPosition = Vector2(0, 0)

    def removeParent(self, gameObject):
        gameObject.transform.children.remove(self.gameObject)
        self.parent = None
        self.localPosition = Vector2(0, 0)

    def getChild(self, index):
        return self.children[index]
