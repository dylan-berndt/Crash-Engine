import os
import sys
import pygame
import tkinter
from tkinter import filedialog
import numpy
from MathBasic import *
import datetime

class Time:
    time = 0
    gameSpeed = 1
    paused = False
    frame = 0
    debugTime = 0
    hooks = []

    @staticmethod
    def startDebugTime():
        Time.debugTime = datetime.datetime.now()

    @staticmethod
    def getDebugTime():
        thing = datetime.datetime.now() - Time.debugTime
        Time.debugTime = datetime.datetime.now()
        return int(thing.microseconds / 1000)

class Editor:
    constantObjects = []
    copied = ""
    sceneView = True
    editObject = None
    terminalActive = False
    terminalList = []
    colliderDraw = True
    triangleDraw = False
    terminalAxis = 0
    drawNormals = False
    normals = []

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
    fileWindow = None

class Input:
    keysDown = []
    unicodeDown = []
    mousePosition = None
    leftClick = False
    rightClick = False
    justPressed = []

    @staticmethod
    def isKeyDown(key):
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
