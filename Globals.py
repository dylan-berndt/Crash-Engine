import os
import sys
import pygame
import numpy
from MathBasic import *

class Time:
    time = 0
    gameSpeed = 1
    paused = False
    frame = 0

class Editor:
    constantObjects = []
    copied = ""
    sceneView = False
    editObject = None
    terminalActive = False
    terminalList = []

class Canvas:
    mainCamera = None
    main = None
    pixelsPerUnit = 0
    screenSize = Vector2(0, 0)
    drawn = False
    sprites = []

    pygame.font.init()
    defaultFont = pygame.font.SysFont("Calibri", 16)

class Resources:
    gameObjects = []
    resourceLocation = ""

class Input:
    keysDown = []
    unicodeDown = []
    mousePosition = None
    leftClick = False
    rightClick = False
    justPressed = []

    def isKeyDown(self, key):
        return key in Input.keysDown or key in Input.unicodeDown

from ObjectManager import *
from FileManager import *
from ScreenManager import *
from PhysicsManager import *
from SceneManager import *
import copy

def init():
    configList = open(os.path.join("config.txt"), "r").read().split("\n")
    Resources.resourceLocation = configList[0]
    Canvas.pixelsPerUnit = int(configList[1])

    sys.path.append(Resources.resourceLocation)

    for i in range(2, len(configList)):
        eval(configList[i])

init()
