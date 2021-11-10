from Globals import *
import Globals


class TitleScreen:
    def __init__(self):
        self.gameObject = None
        self.alpha = 255
        self.hangTime = 3

    def update(self, fpsDelta, gameInput):
        if self.hangTime > 0 and self.alpha > 0:
            self.hangTime -= fpsDelta
        elif self.alpha < 1:
            loadScene("test")
        else:
            self.alpha -= fpsDelta * 100

            logoRenderer = self.gameObject.getComponent(SpriteRenderer)
            newSprite = logoRenderer.sprite.copy().convert()
            newSprite.set_alpha(max(int(self.alpha), 0))
            logoRenderer.sprite = newSprite
