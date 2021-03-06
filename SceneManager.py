from Globals import *
from ObjectManager import *


global sceneList

def addScene(dictionary):
    global sceneList

    try:
        sceneList.append(dictionary)
    except NameError as error:
        sceneList = []
        sceneList.append(dictionary)


def loadScene(sceneName):
    global sceneList

    log(" ")
    log("Loading scene: " + sceneName)
    log("~"*60)

    Time.paused = False
    Resources.gameObjects = []
    for gameObject in Editor.constantObjects:
        Resources.gameObjects.append(gameObject)
    Canvas.sprites = []
    Physics.colliders = []

    sceneFound = False
    sceneLoaded = False

    for scene in sceneList:
        if scene["name"] == sceneName:
            sceneFound = True
            Time.gameSpeed = 1
            if os.path.exists(Resources.resourceLocation + "Scenes\\"+scene["gameObjects"]):
                for line in open(os.path.join(Resources.resourceLocation + "Scenes\\"+scene["gameObjects"])).read().split("\n"):
                    if line != "":
                        exec(line)
                sceneLoaded = True

    for camera in GameObject.getAllWithComponent(Camera):
        if camera.getComponent(Camera).mainCamera:
            Canvas.mainCamera = camera

    if not sceneFound:
        raise NameError("Scene: "+sceneName+" could not be found")
    elif not sceneLoaded:
        raise NameError("Scene: "+sceneName+" had problems loading")

    if len(Editor.constantObjects) == 0:
        fpsDisplay = GameObject(toWorldPos(Vector2(5, 5)), 0, "fpsDisplay")
        fpsDisplay.addComponent(Text(Canvas.defaultFont, "", highlight=(0, 0, 0)))
        Editor.constantObjects.append(fpsDisplay)

        rowHeight = (Canvas.defaultFont.get_height() + 10)
        terminalInput = GameObject(toWorldPos(Vector2(5, Canvas.screenSize.y - rowHeight + 6)), 0, "terminalInput")
        terminalInput.addComponent(
            TextField(font=Canvas.defaultFont, size=Vector2(Canvas.screenSize.x - 10, rowHeight), function=runTerminal))
        terminalInput.active = False
        Editor.constantObjects.append(terminalInput)
