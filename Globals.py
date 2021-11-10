import os
import sys
import pygame
import numpy
from MathBasic import *

class Time:
    time = 0
    gameSpeed = 1
    paused = False

class Editor:
    sceneView = False
    editObject = None

class Canvas:
    mainCamera = None
    main = None
    pixelsPerUnit = 0
    screenSize = Vector2(0, 0)

    pygame.font.init()
    defaultFont = pygame.font.SysFont("Calibri", 16)

class Resources:
    gameObjects = []
    resourceLocation = ""

import ObjectManager
from ObjectManager import *
import ScreenManager
from ScreenManager import *
import PhysicsManager
from PhysicsManager import *
import FileManager
from FileManager import *
import SceneManager
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
