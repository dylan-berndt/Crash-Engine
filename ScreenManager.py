from Globals import *
from ObjectManager import *
from PhysicsManager import *


def toScreenPos(position):
    return (position - Canvas.mainCamera.transform.position) + (Canvas.screenSize / 2)


class Camera:
    def __init__(self, mainCamera=False):
        self.gameObject = None

        self.mainCamera = mainCamera

    def update(self, fpsDelta):
        pass

    def setMainCamera(self):
        for camera in GameObject.getAllWithComponent(Camera):
            camera.mainCamera = False
        self.mainCamera = True
        Canvas.mainCamera = self.gameObject


class Animator:
    def __init__(self):
        pass

    def update(self, fpsDelta):
        pass


class Animation:
    def __init__(self, spriteFolder=None, spriteIndexes=None):
        pass


class SpriteRenderer:
    def __init__(self):
        pass

    def update(self, fpsDelta):
        pass


class Text:
    def __init__(self, font=None, text="", highlight=None, color=(255, 255, 255)):
        self.gameObject = None

        self.font = font
        self.text = text
        self.highlight = highlight
        self.color = color

    def update(self, fpsDelta):
        if self.font is not None:
            Canvas.main.blit(self.font.render(self.text, False, self.color, self.highlight),
                             toScreenPos(self.gameObject.transform.position).toList())


class Button:
    def __init__(self):
        pass

    def update(self, fpsDelta):
        pass
