import pygame
from sylia.renderobject import RenderObject

class Image:

    surface = None
    drawLock = None
    drawList = None

    # This is called internally
    def init(surface, drawLock, drawList):
        Image.surface = surface
        Image.drawLock = drawLock
        Image.drawList = drawList

    def load(imgfile):
        file_location = "{}".format(imgfile)
        image = pygame.image.load(file_location)
        rect = image.get_rect()
        renderobject = RenderObject(image, rect, imgfile)
        return renderobject