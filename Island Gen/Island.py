import pygame
import numpy
from MathBasic import *
from perlin import *

colors = []
mapSize = Vector2(200, 200)
islandMap = numpy.zeros(mapSize.toList())

perlin = Perlin(6789)

noiseLayers = [1, 0.5, 0.01]

def gray(im):
    im = 255 * (im / im.max())
    w, h = im.shape
    ret = numpy.empty((w, h, 3), dtype=numpy.uint8)
    ret[:, :, 2] = ret[:, :, 1] = ret[:, :, 0] = im
    return ret

def generateNoiseMap():
    mapList = []
    for i in range(len(noiseLayers)):
        newMap = numpy.zeros(mapSize.toList())
        mapList.append(newMap)

    for y in range(mapSize.y):
        for x in range(mapSize.x):
            for n, noiseAmplitude in enumerate(noiseLayers):
                mapList[n][y, x] = perlin.two(x * noiseAmplitude, y * noiseAmplitude)

    return mapList

noiseMaps = generateNoiseMap()
for map in noiseMaps:
    islandMap += map

islandSurface = pygame.transform.scale(pygame.surfarray.make_surface(gray(islandMap)), (mapSize * 3).toList())

main = pygame.display.set_mode((mapSize * 4).toList())

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

    main.blit(islandSurface, (((mapSize * 4) - (mapSize * 3)) / 2).toList())

    pygame.display.update()

