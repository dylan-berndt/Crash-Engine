import copy

from Globals import *


def instantiate(original, name, active=True, position=None):
    new = copy.deepcopy(original)
    new.name, new.active = name, active
    if position is not None:
        new.transform.position = position
    return new


def destroy(gameObject):
    Resources.gameObjects.remove(gameObject)
    for component in gameObject.components:
        if hasattr(component, "destroy"):
            component.destroy()
        del component
    del gameObject


class GameObject:
    def __init__(self, position, name, rotation=0):
        self.transform = Transform(position, rotation)
        self.name = name
        self.components = [self.transform]
        self.active = True

        Resources.gameObjects.append(self)

    def update(self, fpsDelta):
        for component in self.components:
            component.gameObject = self
            component.update(fpsDelta)

        for component in self.components:
            if hasattr(component, "late_update"):
                component.late_update(fpsDelta)

    def addComponent(self, component):
        self.components.append(component)
        return self

    def removeComponent(self, component):
        self.components.remove(component)
        if component in Physics.colliders:
            Physics.colliders.remove(component)
        del component

    def getComponent(self, componentType):
        for component in self.components:
            if type(component) == componentType:
                return component

    def getComponents(self, componentType):
        for component in self.components:
            if type(component) == componentType:
                yield component

    def getComponentsOfTypes(self, componentTypes):
        for component in self.components:
            if type(component) in componentTypes:
                yield component

    @staticmethod
    def find(name):
        for gameObject in Resources.gameObjects:
            if gameObject.name == name:
                return gameObject

    @staticmethod
    def getEveryComponentOfType(componentType):
        for gameObject in Resources.gameObjects:
            if gameObject.getComponent(componentType) is not None:
                for component in gameObject.getComponents(componentType):
                    yield component

    @staticmethod
    def getEveryComponentOfTypes(componentTypes):
        for gameObject in Resources.gameObjects:
            for component in gameObject.components:
                if component in componentTypes:
                    yield component


class Transform:
    def __init__(self, position, rotation=0, scale=None):
        self.gameObject = None

        self.position = position
        self.rotation = rotation
        self.scale = scale if scale is not None else Vector2(1, 1)

    def localToWorld(self, point):
        return (point * self.scale) + self.position

    def localToScreen(self, point):
        return Transform.worldToScreen(self.localToWorld(point))

    def update(self, fpsDelta):
        pass

    @staticmethod
    def worldToScreen(point):
        return ((point - Screen.camera.gameObject.transform.position) * Screen.unit) + (Screen.size / 2)
