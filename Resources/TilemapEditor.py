import Globals
from Globals import *

class TilemapEditor:
    def __init__(self):
        self.gameObject = None

        self.currentDirectory = None

        self.points = []
        self.tiles = []
        self.image = None
        self.imageTiles = []

    def update(self, fpsDelta):
        text = self.gameObject.getComponent(Text)

        if Input.isKeyDown(pygame.K_RETURN):
            self.currentDirectory = openFile([(".png files", "*.png"), (".jpg files", "*.jpg")], "Open Tilemap Image")
            directoryWorks = True
            load = None
            if self.currentDirectory != "":
                load = loadSprite(self.currentDirectory, absolutePath=True)
            else:
                directoryWorks = False
            if load is None:
                directoryWorks = False

            if directoryWorks:
                self.image = load

            if not directoryWorks:
                self.currentDirectory = None
                self.image = None

        if text is None:
            self.gameObject.addComponent(Text(offset=Vector2(0, 1), orientation=Vector2(1, 2)))
        else:
            if self.currentDirectory is None:
                text.text = "Press Enter to open image"
            else:
                text.text = self.currentDirectory
                text.offset = toWorldPos(Vector2(5, Canvas.screenSize.y - 2))
                text.orientation = Vector2(0, 2)

    def addTile(self):
        pass

    def loadMap(self):
        pass

    def loadImage(self):
        pass
