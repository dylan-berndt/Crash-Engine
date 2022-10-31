from Globals import *


class Camera:
    def __init__(self, mainCamera=False):
        self.gameObject = None
        self.mainCamera = mainCamera
        if Screen.camera is None:
            Screen.camera = self
        Resources.cameras.append(self)

    def update(self, fpsDelta):
        pass

    def setMain(self):
        for camera in Resources.cameras:
            camera.mainCamera = False
        self.mainCamera = True
        Screen.camera = self


class SpriteRenderer:
    def __init__(self, sprite, order: int = 0, layer="default"):
        self.gameObject = None

        self.sprite = sprite

        self.order = order
        self.layer = layer
        self.renderGroup = None
        self.renderLayer = None

        self.allSprites = [sprite]

        self.getRenderData()

    def destroy(self):
        for sprite in self.allSprites:
            sprite.delete()

    def getRenderData(self):
        layer = Screen.renderGroups[self.layer]
        if str(self.order) in layer["groups"]:
            self.renderGroup = layer["groups"][str(self.order)]
        else:
            self.renderGroup = pyglet.graphics.OrderedGroup(self.order)
        if self.layer == "widgets" or self.layer == "console":
            print("Cannot add objects to", self.layer, "layer, using default")
            self.layer = "default"
        self.renderLayer = layer["batch"]

        self.sprite.batch = self.renderLayer
        self.sprite.group = self.renderGroup

        return self.renderGroup, self.renderLayer

    def setRenderData(self, order: int = None, layer=None):
        self.order = self.order if order is None else order
        self.layer = self.layer if layer is None else layer
        self.getRenderData()

    def update(self, fpsDelta):
        pass

    def late_update(self, fpsDelta):
        self.spritePosition()

    def spritePosition(self):
        if self.gameObject is not None:
            sprite, transform = self.sprite, self.gameObject.transform

            sprite.scale_x = transform.scale.x * (Screen.unit / self.sprite.ppu)
            sprite.scale_y = transform.scale.y * (Screen.unit / self.sprite.ppu)

            position = transform.worldToScreen(transform.position)

            sprite.x = position.x - sprite.width / 2
            sprite.y = position.y - sprite.height / 2

    def setSprite(self, sprite):
        self.sprite.batch = None
        self.sprite = sprite
        if sprite not in self.allSprites:
            self.allSprites.append(sprite)
        self.spritePosition()
        self.getRenderData()


class Sprite(pyglet.sprite.Sprite):
    def __init__(self, spritePath, ppu=Screen.unit):
        super(Sprite, self).__init__(pyglet.image.load(os.path.join(Resources.resourcePath, spritePath)))
        self.path = spritePath
        self.ppu = ppu

    def __reduce__(self):
        return [(type(self)), {self.path: self.path}, None, None]


class Frame:
    def __init__(self, startTime=0, value=None, valueName="", interpolation=lerp, operation="set"):
        self.time = startTime
        self.value = value
        self.component = None
        self.valueName = valueName
        self.interpolation = interpolation
        self.operation = operation

    def enact(self, animator, nextFrame=None, timeLerp=0):
        value = self.value
        if type(self.value) in [int, float] and self.interpolation == lerp and nextFrame is not None:
            value = lerp(self.value, nextFrame.value, timeLerp)
        if self.operation == "set":
            if hasattr(self.component, self.valueName):
                setattr(self.component, self.valueName, value)
            else:
                self.component = animator.component
                setattr(self.component, self.valueName, value)
        elif self.operation == "func":
            if hasattr(self.component, self.valueName):
                getattr(self.component, self.valueName)(value)
            else:
                self.component = animator.component
                getattr(self.component, self.valueName)(value)


class Animation:
    def __init__(self, frames=None, loop=True):
        self.gameObject = None
        self.frames = frames if frames is not None else []
        self.currentIndex = 0
        self.time = 0
        self.loop = loop

    def update(self, fpsDelta, animator):
        self.time += fpsDelta
        if self.frames:
            totalTime = self.frames[-1].time
            for f, frame in enumerate(self.frames):
                if self.time < frame.time and f >= self.currentIndex:
                    self.currentIndex = f
                    timeLerp = frame.time - self.time
                    if not self.loop:
                        frame.enact(animator, self.frames[max(f, len(self.frames) - 1)], timeLerp)
                    else:
                        frame.enact(animator, self.frames[(f + 1) % len(self.frames)], timeLerp)
                    break
            if self.time > totalTime:
                self.time = self.time % totalTime
                self.currentIndex = 0
                self.frames[0].enact(animator)

    def attachTo(self, component, valueName):
        for frame in self.frames:
            frame.component = component
            frame.valueName = valueName


def animationFromFolder(spriteFolder, fps):
    sprites = [Sprite(spriteFolder + name) for name in os.listdir(os.path.join(Resources.resourcePath, spriteFolder))]
    return createSpriteAnimation(sprites, range(len(sprites)), fps)


def createSpriteAnimation(sprites, indexes, fps):
    frames = []
    for i, index in enumerate(indexes):
        frames.append(Frame((i + 1) * (1/fps), sprites[index], valueName="setSprite", operation="func"))
    animation = Animation(frames)
    return animation


class Animator:
    def __init__(self, animations=None, initialState="", component=None):
        self.gameObject = None
        self.state = initialState
        self.animations = animations if animations is not None else {}
        self.animation = self.animations[self.state] if self.animations else None
        self.component = component

    def update(self, fpsDelta):
        if self.animation is not None:
            self.animation.update(fpsDelta, self)

    def setState(self, name):
        self.state = name
        self.animation = self.animations[self.state]

    def addAnimation(self, name, animation):
        self.animations[name] = animation
