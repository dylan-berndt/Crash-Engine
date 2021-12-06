import Globals
from Globals import *

Canvas.screenSize = Vector2(1280, 640)
Canvas.main = pygame.display.set_mode(Canvas.screenSize.toList())
pygame.display.set_caption("Crash Engine")
clock = pygame.time.Clock()

pygame.init()

loadScene("polygon")

while True:
    Canvas.main.fill((0, 0, 0))

    mx, my = pygame.mouse.get_pos()
    mousePosition = Vector2(mx, my)

    clock.tick(360)
    fps = clock.get_fps()
    if fps != 0:
        update(1 / fps)
        manageInput(1 / fps, pygame.event.get(), mousePosition)

    pygame.display.update()
