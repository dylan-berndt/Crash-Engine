from Globals import *
from FileManager import *
from ScreenManager import *
from PhysicsManager import *


def runTerminal(string):
    if string != "":
        for command in string.split("&"):
            while command[0] == " ":
                command = command[1:]
            try:
                GameObject.Find("terminalInput").getComponent(TextField).text = ""
                exec(command)
            except Exception as e:
                log(" ")
                log(str(type(e).__name__) + ": " + str(e))

def log(string):
    rowHeight = (Canvas.defaultFont.get_height() + 4)
    Editor.terminalAxis -= rowHeight
    Editor.terminalList.append(str(string))

def manageInput(fpsDelta, events, mousePosition):
    Input.leftClick = False
    Input.rightClick = False
    Input.justPressed = []

    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                Input.leftClick = True
            if event.button == 3:
                Input.rightClick = True

            if Editor.terminalActive:
                if event.button == 4:
                    Editor.terminalAxis += fpsDelta * 2000
                if event.button == 5:
                    Editor.terminalAxis -= fpsDelta * 2000

        if event.type == pygame.KEYDOWN:
            Input.keysDown.append(event.key)
            Input.unicodeDown.append(event.unicode)
            Input.justPressed.append(event.unicode)

            if event.key == pygame.K_BACKSLASH and pygame.key.get_mods() & pygame.KMOD_SHIFT:
                Editor.sceneView = not Editor.sceneView
                if not Editor.sceneView:
                    Editor.terminalActive = False

            if Editor.sceneView:
                if event.key == pygame.K_ESCAPE:
                    Editor.terminalAxis = 0
                    Editor.terminalActive = not Editor.terminalActive

                if Editor.terminalActive:
                    if event.key == pygame.K_c and pygame.key.get_mods() & pygame.KMOD_CTRL:
                        Editor.copied = GameObject.Find("terminalInput").getComponent(TextField).text

                    if event.key == pygame.K_v and pygame.key.get_mods() & pygame.KMOD_CTRL:
                        GameObject.Find("terminalInput").getComponent(TextField).text += Editor.copied

                    if event.key == pygame.K_TAB:
                        log(" ")
                        log("Current GameObjects: ")
                        for gameObject in Resources.gameObjects:
                            log(gameObject.name + " | active: " + str(gameObject.active))

                else:
                    if event.key == pygame.K_n and pygame.key.get_mods() & pygame.KMOD_CTRL:
                        Editor.drawNormals = not Editor.drawNormals

                    if event.key == pygame.K_p and pygame.key.get_mods() & pygame.KMOD_CTRL:
                        Time.paused = not Time.paused

                    if event.key == pygame.K_t and pygame.key.get_mods() & pygame.KMOD_CTRL:
                        Editor.triangleDraw = not Editor.triangleDraw

                    if event.key == pygame.K_c and pygame.key.get_mods() & pygame.KMOD_CTRL:
                        Editor.colliderDraw = not Editor.colliderDraw

                    if pygame.key.get_mods() & pygame.KMOD_SHIFT and Input.leftClick:
                        pass

        if event.type == pygame.KEYUP:
            Input.keysDown.remove(event.key)
            Input.unicodeDown.remove(event.unicode)

        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
    Input.mousePosition = mousePosition

def updateEditor(fpsDelta):
    if Editor.sceneView:
        if Input.isKeyDown(pygame.K_w):
            Canvas.pixelsPerUnit *= 1 + fpsDelta

        if Input.isKeyDown(pygame.K_s):
            Canvas.pixelsPerUnit /= 1 + fpsDelta

        GameObject.Find("fpsDisplay").getComponent(Text).text = "FPS: " + str(round(10/fpsDelta) / 10)
        totalEnergy = sum(collider.rigidbody.velocity.magnitude() * collider.rigidbody.mass for collider in Physics.colliders)

        rowHeight = (Canvas.defaultFont.get_height() + 4)

        if not Editor.terminalActive:
            if Editor.drawNormals:
                for normal in Editor.normals[-100:]:
                    drawPoint = toScreenPos(normal[0])
                    pygame.draw.line(Canvas.main, (255, 255, 255), drawPoint.toList(), (drawPoint + (normal[1] * 10)).toList())

            for gameObject in list(set(Resources.gameObjects) - set(Editor.constantObjects)):
                pygame.draw.circle(Canvas.main, (255, 255, 255), toScreenPos(gameObject.transform.position).toList(), 2, 1)

                if gameObject.getComponent(Rigidbody) is not None:
                    if Editor.colliderDraw:
                        pygame.draw.circle(Canvas.main, (255, 0, 0), toScreenPos(gameObject.getComponent(Rigidbody).center).toList(), 5, 1)

                    velocityPos = gameObject.getComponent(Rigidbody).velocity * 5 * (Canvas.pixelsPerUnit / 25)
                    pygame.draw.line(Canvas.main, (255, 0, 0), toScreenPos(gameObject.transform.position).toList(),
                                     (toScreenPos(gameObject.transform.position) + Vector2(velocityPos.x, 0)).toList())
                    pygame.draw.line(Canvas.main, (0, 0, 255), toScreenPos(gameObject.transform.position).toList(),
                                     (toScreenPos(gameObject.transform.position) + Vector2(0, velocityPos.y)).toList())

                colliders = gameObject.getAllOfComponentTypes(Physics.colliderTypes)
                for collider in colliders:
                    if Editor.colliderDraw and not Editor.triangleDraw:
                        pointList = list(toScreenPos(point).toList() for point in collider.points)
                        if len(pointList) > 1:
                            pygame.draw.polygon(Canvas.main, (0, 255, 0), pointList, 1)

                    if Editor.triangleDraw:
                        lineList = []
                        for l in range(len(collider.lines)):
                            thing = list(toScreenPos(line[0]).toList() for line in collider.lines[l][:-2])
                            for t in thing:
                                lineList.append(t)
                        pygame.draw.polygon(Canvas.main, (0, 255, 0), lineList, 1)

            for gameObject in list(set(Resources.gameObjects) - set(Editor.constantObjects)):
                if Input.mousePosition is not None:
                    if Vector2.distance(Input.mousePosition, toScreenPos(gameObject.transform.position)) < 60:
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
            mockTerminal = pygame.Surface((boxWidth, totalHeight))
            for t, text in enumerate(Editor.terminalList):
                mockTerminal.blit(Canvas.defaultFont.render(text, True, (255, 255, 255)),
                                  (5, (t * rowHeight)))

            Canvas.main.blit(mockTerminal, (0, Editor.terminalAxis), (0, 0, boxWidth, (boxHeight - (2 * rowHeight)) - Editor.terminalAxis))

        terminalInput = GameObject.Find("terminalInput")
        terminalInput.active = Editor.terminalActive
        terminalInput.getComponent(TextField).focused = Editor.terminalActive
        if Editor.terminalActive:
            terminalInput.transform.position = toWorldPos(Vector2(5, Canvas.screenSize.y - rowHeight))
            terminalInput.update(fpsDelta)
        fpsDisplay = GameObject.Find("fpsDisplay")
        fpsDisplay.transform.position = toWorldPos(Vector2(5, 5))
        fpsDisplay.update(fpsDelta)


def update(fpsDelta):
    stillDelta = fpsDelta
    if Time.paused:
        fpsDelta = 0

    fpsDelta *= Time.gameSpeed

    Time.time += fpsDelta
    Time.frame += 1

    Canvas.drawn = False

    for gameObject in Resources.gameObjects:
        if gameObject.active and gameObject.name != "terminalInput" and gameObject.name != "fpsDisplay":
            gameObject.update(fpsDelta)

    updateEditor(stillDelta)


def addComponent(component):
    Resources.gameObjects[-1].addComponent(component)


def getComponent(component):
    return Resources.gameObjects[-1].getComponent(component)


def removeComponent(componentType):
    Resources.gameObjects[-1].removeComponent(componentType)


def instantiate(gameObject, active=True, position=None):
    endPosition = position if position is not None else gameObject.transform.position

    newObject = recreate(gameObject)
    newObject.components = []
    for component in gameObject.components:
        newComponent = recreate(component)
        newComponent.gameObject = newObject
        newObject.components.append(newComponent)
    newObject.active = active
    newObject.transform.position = endPosition
    log(" ")
    log("Created new instance of " + gameObject.name + " at " + str(endPosition))
    return newObject


class GameObject:
    def __init__(self, position=None, rotation=0, name=""):
        self.name = name
        self.transform = Transform(position if position is not None else Vector2(0, 0),
                                   rotation)
        self.components = [self.transform]
        self.active = True
        if name != "" or position is not None:
            log(" ")
            log("Created GameObject " + name + " at " + str(position))
        Resources.gameObjects.append(self)

    def update(self, fpsDelta):
        for component in self.components:
            component.update(fpsDelta)

    def addComponent(self, component):
        self.components.append(component)
        log("Added " + str(type(component).__name__) + " to " + self.name)
        component.gameObject = self

    def removeComponent(self, componentType):
        for component in self.components:
            if type(component) == componentType:
                self.components.remove(component)
                break

    def getComponent(self, componentType):
        for component in self.components:
            if type(component) == componentType:
                return component

    def getAllOfComponentTypes(self, componentTypes):
        return list(component for component in self.components if type(component) in componentTypes)

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

#this is the only comment im gonna make until it's time to publish this
#thing and i just wanna say that it's 3:50 am and i am so goddamn annoyed
#that i have to do this like this i've tried 8 other ways to import shit
#so that you can load scenes in the terminal but nothing works and i've
#had it up to here so fuck you and fuck your kids this looks stupid
#but i'm doing it anyways fuck you goodnight also im drunk
from SceneManager import *
