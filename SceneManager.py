from Globals import *


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

    Time.paused = False
    Resources.gameObjects = []
    Canvas.sprites = []

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

    fpsDisplay = GameObject(toWorldPos(Vector2(5, 5)), 0, "fpsDisplay")
    fpsDisplay.addComponent(Text(Canvas.defaultFont, "", highlight=(0, 0, 0)))
    fpsDisplay.transform.setParent(Canvas.mainCamera)
