import copy

from Globals import *


def instantiate(original, name, active=True, position=None):
    new = copy.deepcopy(original)
    new.name, new.active = name, active
    if position is not None:
        new.transform.position = position
    Resources.gameObjects.append(new)
    return new


def destroy(gameObject):
    Resources.gameObjects.remove(gameObject)
    for component in gameObject.components:
        component.destroy()
        del component
    del gameObject


class GameObject:
    def __init__(self, position, name, rotation=0, active=True):
        self.transform = Transform(position, rotation)
        self.name = name
        self.components = [self.transform]
        self.active = active

        self._keep = False

        Resources.gameObjects.append(self)

    def __str__(self):
        return "GameObject: " + self.name + " " + str(self.transform.position)

    @property
    def keep(self):
        return self._keep

    @keep.setter
    def keep(self, k):
        self._keep = k
        if k:
            Resources.keep.append(self)
        else:
            Resources.keep.remove(self)

    def update(self, fpsDelta):
        if self.active:
            for component in self.components:
                component.gameObject = self
                component.update(fpsDelta)

    def late_update(self, fpsDelta):
        for component in self.components:
            component.late_update(fpsDelta)

    def on_mouse_click(self, x, y, button, modifiers):
        for component in self.components:
            component.on_mouse_click(x, y, button, modifiers)

    def on_mouse_release(self, x, y, button, modifiers):
        for component in self.components:
            component.on_mouse_release(x, y, button, modifiers)

    def on_mouse_motion(self, x, y, dx, dy):
        for component in self.components:
            component.on_mouse_motion(x, y, dx, dy)

    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        for component in self.components:
            component.on_mouse_drag(x, y, dx, dy, button, modifiers)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        for component in self.components:
            component.on_mouse_scroll(x, y, scroll_x, scroll_y)

    def on_key_press(self, symbol, modifiers):
        for component in self.components:
            component.on_key_press(symbol, modifiers)

    def on_key_release(self, symbol, modifiers):
        for component in self.components:
            component.on_key_release(symbol, modifiers)

    def addComponent(self, *args):
        for component in args:
            if not isinstance(component, Component):
                continue
            self.components.append(component)
            component.gameObject = self
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
            if type(componentType) == str:
                if type(component).__name__ == componentType:
                    return component

    def getComponents(self, componentType):
        for component in self.components:
            if type(component) == componentType:
                yield component
            if type(componentType) == str:
                if type(component).__name__ == componentType:
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


class Transform(Component):
    def __init__(self, position, rotation=0, scale=None):
        self.gameObject = None

        self.localPosition = None
        self.position = position
        self.rotation = rotation
        self.scale = scale if scale is not None else Vector2(1, 1)

        self._children = []
        self._parent = None

    def destroy(self):
        for child in self._children:
            destroy(child.gameObject)

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, parent):
        self._parent = parent
        parent.addChild(self)

    def addChild(self, child):
        self._children.append(child)
        child.localPosition = child.position - self.position

    def removeChild(self, child):
        self._children.remove(child)
        child.localPosition = None

    def localToWorld(self, point):
        return (point * self.scale) + self.position

    def localToScreen(self, point):
        return Transform.worldToScreen(self.localToWorld(point))

    def update(self, fpsDelta):
        for child in self._children:
            child.position = self.position + child.localPosition

    @staticmethod
    def worldToScreen(point):
        return ((point - Screen.camera.gameObject.transform.position) * Screen.unit) + (Screen.size / 2)

    @staticmethod
    def screenToWorld(point):
        return (point - (Screen.size / 2) / Screen.unit) + Screen.camera.gameObject.transform.position
