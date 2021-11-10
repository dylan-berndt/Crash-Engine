import pygame
from MathBasic import *
import random
import math
import colorsys
import os

totalPoints = 60
pointList = []
circleThickness = 3
hueShift = 0
seconds = 2

prevLists = []

mouseMode = True
autoMode = False
colorMode = True
colorType = "hue"
screenSize = Vector2(1200, 800)

loadFile = ""

if loadFile == "":
    angle = 0
    for i in range(totalPoints):
        angle += 360/totalPoints
        circlePosition = Vector2(math.sin(math.radians(angle)), math.cos(math.radians(angle)))
        pointList.append((screenSize / 2) + (circlePosition * (min(screenSize.x/2, screenSize.y/2) - 100)))
else:
    file = open(loadFile, "r")
    pointList = eval(file.readlines()[0])
    pointList = list(toVector(pointList[i]) for i in range(len(pointList)))


bezierList = []
t = 0
counter = 0

def lerp(point1, point2, t):
    return point1 + ((point2 - point1) * t)

pygame.init()

calibri = pygame.font.SysFont("Calibri", 12, False)

main = pygame.display.set_mode(screenSize.toList())
clock = pygame.time.Clock()

clicking = False
fullscreen = False
tDot = 0
tMin = False
tMax = False

while True:
    main.fill((0, 0, 0))

    mx, my = pygame.mouse.get_pos()

    pygame.draw.lines(main, (100, 100, 100), False, (tuple(pointList[i].toList() for i in range(len(pointList)))), 3)

    linesLeft = len(pointList)-1
    lineList = list([pointList[i], pointList[i+1]] for i in range(len(pointList)-1))
    while linesLeft > 1:
        addLines = []
        for l, line in enumerate(lineList):
            if len(lineList) - 1 > l >= len(lineList) - linesLeft:
                point1 = lerp(line[0], line[1], t)
                point2 = lerp(lineList[l+1][0], lineList[l+1][1], t)
                newLine = [point1, point2]
                addLines.append(newLine)
        for line in addLines:
            lineList.append(line)
        linesLeft -= 1

    if colorMode:
        numDivs = 0
        divsLeft = len(lineList)
        divList = []
        while divsLeft > 0:
            currentDivSize = (len(pointList) - 1) - numDivs
            divsLeft -= currentDivSize
            for i in range(currentDivSize):
                divList.append(currentDivSize)
            numDivs += 1

        for l, line in enumerate(lineList):
            hue = divList[l] / numDivs
            if colorType == "hue":
                hue = wrap(hue + hueShift, 0, 1)
                rgb = colorsys.hsv_to_rgb(hue, 1, 1)
            elif colorType == "blue":
                blueColors = [Vector3(66, 135, 245)/255, Vector3(199, 46, 196)/255]
                rgb = lerp(blueColors[0], blueColors[1], hue).toList()
            elif colorType == "due":
                rgb = lerp(Vector3(1, 1, 1), Vector3(0.1, 0.1, 0.1), hue).toList()
            else:
                rgb = colorsys.hsv_to_rgb(hue, 1, 1)
            pygame.draw.line(main, list(rgb[i] * 255 for i in range(len(rgb))), line[0].toList(), line[1].toList(), 2)

    else:
        for l, line in enumerate(lineList):
            pygame.draw.line(main, (255, 255, 255), line[0].toList(), line[1].toList(), 2)

    fps = clock.get_fps()

    if not (tMin and tMax) and counter != 0:
        bezierList.append(lerp(lineList[-1][0], lineList[-1][1], t))
    elif (tMin and tMax) and autoMode:
        counter = 0
        tMin = False
        tMax = False
        random.shuffle(pointList)
        while pointList in prevLists and math.factorial(len(pointList)) < len(prevLists):
            random.shuffle(pointList)
        prevLists.append(pointList)

    if clicking and mouseMode:
        circleSize = min(screenSize.x, screenSize.y) - 200
        barPos = (screenSize.x - circleSize) / 2
        tDot = max(min((mx - barPos), circleSize), 0)
        t = tDot / circleSize

    if autoMode:
        t = (math.sin(counter + (math.pi / 2)) / 2) + 0.5
        if fps != 0:
            counter += (1/seconds) / fps

    if t < 0.0001:
        tMin = True
    if t > 0.9999:
        tMax = True

    for point in bezierList:
        pygame.draw.circle(main, (255, 255, 255), point.toList(), circleThickness)

    tText = calibri.render(str(round(t*100)/100), True, (255, 255, 255))

    if mouseMode:
        circleSize = min(screenSize.x, screenSize.y) - 200
        barPos = (screenSize.x - circleSize) / 2
        barLow = (screenSize.y - circleSize) * 0.75 + circleSize
        pygame.draw.rect(main, (50, 50, 50), (barPos, barLow - 5, circleSize, 10))
        pygame.draw.circle(main, (50, 50, 50), (barPos, barLow), 5)
        pygame.draw.circle(main, (50, 50, 50), (barPos + circleSize, barLow), 5)
        pygame.draw.circle(main, (255, 255, 255), (tDot + barPos, barLow), 12)
        pygame.draw.circle(main, (100, 100, 250), (tDot + barPos, barLow), 10)

    color = (255, 0, 0)
    if colorType == "hue":
        color = (255, 0, 0)
    elif colorType == "blue":
        color = (0, 0, 255)
    elif colorType == "due":
        color = (255, 255, 255)
    pygame.draw.circle(main, color, (screenSize / 2).toList(), (min(screenSize.x / 2, screenSize.y / 2) - 100) + 2, 2)

    main.blit(tText, (10, 10))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1  and 730 < my < 780:
                clicking = True

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                clicking = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if fullscreen:
                    main = pygame.display.set_mode(screenSize.toList())
                else:
                    main = pygame.display.set_mode(screenSize.toList(), pygame.FULLSCREEN)
                fullscreen = not fullscreen

            if event.key == pygame.K_BACKSLASH:
                savePath = "Bezier Points.txt"
                saveNum = 1
                while os.path.exists(savePath):
                    savePath = "Bezier Points (" + str(saveNum) + ").txt"
                    saveNum += 1
                textFile = open(savePath, "w")
                textFile.write(str(tuple(pointList[i].round().toList() for i in range(len(pointList)))))

            if event.key == pygame.K_RETURN:
                pointList = []
                bezierList = []
                counter = 0
                tMin = False
                tMax = False
                for i in range(totalPoints):
                    angle = random.randint(0, 360)
                    circlePosition = Vector2(math.sin(math.radians(angle)), math.cos(math.radians(angle)))
                    pointList.append((screenSize / 2) + (circlePosition * (min(screenSize.x / 2, screenSize.y / 2) - 100)))

    clock.tick(240)
    pygame.display.update()