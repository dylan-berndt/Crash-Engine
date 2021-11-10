from Globals import *
from ObjectManager import *
from PhysicsManager import *
from FileManager import *


def toScreenPos(position):
    return ((position - Canvas.mainCamera.transform.position) * Canvas.pixelsPerUnit) + (Canvas.screenSize / 2)

def toWorldPos(position):
    return ((position - (Canvas.screenSize / 2)) / Canvas.pixelsPerUnit) + Canvas.mainCamera.transform.position


class Camera:
    def __init__(self, mainCamera=False, aspectRatio=None):
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
    def __init__(self, spriteName="", scale=1, tiling=None, drawOrder=0):
        self.gameObject = None

        self.sprite = loadSprite(spriteName) if spriteName is not "" else None
        self.drawSprite = None
        self.scale = scale
        self.size = None
        self.tiling = tiling if tiling is not None else Vector2(1, 1)
        self.drawOrder = drawOrder

    def reloadSprite(self):
        self.sortSprite()

        imageSize = Vector2(self.sprite.get_width(), self.sprite.get_height())
        self.size = imageSize * self.scale
        drawSurface = pygame.Surface((imageSize * self.tiling * self.scale).toList(), pygame.SRCALPHA)
        for y in range(self.tiling.y):
            for x in range(self.tiling.x):
                drawSurface.blit(pygame.transform.scale(self.sprite, self.size.toList()), (x * self.size.x, y * self.size.y))
        self.drawSprite = drawSurface

    def sortSprite(self):
        if not self in Canvas.sprites:
            if Canvas.sprites == []:
                Canvas.sprites.append(self)
            else:
                notAdded = True
                for s, sprite in enumerate(Canvas.sprites):
                    if sprite.drawOrder >= self.drawOrder and notAdded:
                        notAdded = False
                        Canvas.sprites.insert(s % (len(Canvas.sprites) + 1), self)
                if not self in Canvas.sprites:
                    Canvas.sprites.insert(len(Canvas.sprites), self)

    def changeDrawOrder(self, order):
        Canvas.sprites.remove(self)
        self.drawOrder = order
        self.sortSprite()

    def update(self, fpsDelta):
        if self.drawSprite is None:
            self.reloadSprite()

        if not Canvas.drawn:
            for sprite in Canvas.sprites:
                sprite.draw()
            Canvas.drawn = True

    def draw(self):
        if self.gameObject.transform.rotation == 0:
            Canvas.main.blit(self.drawSprite, (toScreenPos(self.gameObject.transform.position) - (self.size / 2)).toList())
        else:
            rotatedSprite = pygame.transform.rotate(self.drawSprite, -self.gameObject.transform.rotation)
            rotateDifference = Vector2(rotatedSprite.get_width() - self.drawSprite.get_width(),
                                       rotatedSprite.get_height() - self.drawSprite.get_height())
            Canvas.main.blit(rotatedSprite,
                             (toScreenPos(self.gameObject.transform.position) - (self.size / 2) - (rotateDifference / 2)).toList())


class Text:
    def __init__(self, font=None, text="", highlight=None, color=(255, 255, 255)):
        self.gameObject = None

        self.font = font
        self.text = text
        self.highlight = highlight
        self.color = color

    def update(self, fpsDelta):
        if self.font is not None:
            Canvas.main.blit(self.font.render(self.text, True, self.color, self.highlight),
                             toScreenPos(self.gameObject.transform.position).toList())


class Button:
    def __init__(self):
        pass

    def update(self, fpsDelta):
        pass
