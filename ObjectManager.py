from Globals import *
from ScreenManager import *
from PhysicsManager import *


def manageInput(events, mousePosition):
    for event in events:
        if event.type == pygame.KEYDOWN:
            Input.keysDown.append(event.key)
            Input.unicodeDown.append(event.unicode)

            if event.key == pygame.K_BACKSLASH and pygame.key.get_mods() & pygame.KMOD_SHIFT:
                Editor.sceneView = not Editor.sceneView

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
        for gameObject in Resources.gameObjects:
            pygame.draw.circle(Canvas.main, (255, 255, 255), toScreenPos(gameObject.transform.position).toList(), 2, 1)

    else:
        GameObject.Find("fpsDisplay").getComponent(Text).text = ""

def update(fpsDelta):
    if Time.paused:
        fpsDelta = 0

    Time.time += fpsDelta

    for gameObject in Resources.gameObjects:
        gameObject.update(fpsDelta)

    updateEditor(fpsDelta)

def addComponent(component):
    Resources.gameObjects[-1].addComponent(component)

def instantiate(gameObject):
    return recreate(gameObject)


class Input:
    keysDown = []
    unicodeDown = []
    mousePosition = None


class GameObject:
    def __init__(self, position=None, rotation=0, name=""):
        self.name = name
        self.transform = Transform(position if position is not None else Vector2(0, 0),
                                   rotation)
        self.components = [self.transform]
        Resources.gameObjects.append(self)

    def update(self, fpsDelta):
        for component in self.components:
            component.update(fpsDelta)

    def addComponent(self, component):
        self.components.append(component)
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
