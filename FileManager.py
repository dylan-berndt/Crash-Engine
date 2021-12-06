from Globals import *
import Globals
import copy


def recreate(copyThing):
    copyobj = type(copyThing)()
    for name, attr in copyThing.__dict__.items():
        if hasattr(attr, 'copy') and callable(getattr(attr, 'copy')):
            copyOther = attr.copy()
            try:
                if copyOther["type"] == "Vector2":
                    copyOther = Vector2(copyOther["x"], copyOther["y"])
                if copyOther["type"] == "Vector3":
                    copyOther = Vector3(copyOther["x"], copyOther["y"], copyOther["z"])
            except KeyError as error:
                pass
            except TypeError as error:
                pass
            copyobj.__dict__[name] = copyOther
        else:
            copyobj.__dict__[name] = copy.deepcopy(attr)
    return copyobj

def openFile(fileTypes=None, title="Open File"):
    top = tkinter.Tk()
    top.withdraw()
    fileName = tkinter.filedialog.askopenfilename(parent=top, initialdir=Resources.resourceLocation, filetypes=fileTypes, title=title)
    top.destroy()
    return fileName

def openFolder():
    pass

def loadSprites(folder, scale=1):
    items = []
    loadList = os.listdir(Resources.resourceLocation + folder)
    for item in loadList:
        if item.endswith(".png") or item.endswith(".jpg"):
            imageLoad = loadSprite(folder + "\\" + item[:-4])
            imageSize = imageLoad.get_rect().size
            imageSize = Vector2(imageSize[0], imageSize[1]) * scale
            items.append(pygame.transform.scale(imageLoad, imageSize.toList()))

    return items


def loadSprite(startName, absolutePath=False):
    if absolutePath:
        name = startName[:-4]
    else:
        name = Resources.resourceLocation + startName
    try:
        return pygame.image.load(os.path.join(name+".png")).convert_alpha()
    except FileNotFoundError:
        try:
            return pygame.image.load(os.path.join(name+".jpg")).convert_alpha()
        except FileNotFoundError:
            if absolutePath:
                print("No image at " + startName[:-4])
            else:
                print("No image named " + startName + " at " + Resources.resourceLocation)


def loadMaterial(name):
    name = Resources.resourceLocation + name
    try:
        materialFile = open(name + ".mat", "r")
        fileLines = materialFile.read().split("\n")
        bounce = float(fileLines[0])
        friction = float(fileLines[1])
        return PhysicsMaterial(bounce, friction)
    except FileNotFoundError:
        print("No material at: " + name)
        return PhysicsMaterial()
