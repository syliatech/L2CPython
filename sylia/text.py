import pygame
from sylia.renderobject import RenderObject

class Text:
    
    fonts = {}
    surface = None
    drawLock = None
    drawList = None

    # This is called internally
    def init(surface, drawLock, drawList):
        Text.surface = surface
        Text.drawLock = drawLock
        Text.drawList = drawList

    # Will load a custom font into fonts dictionary
    def __loadFont(fontName, size, fontFile):

        #Check if we have already loaded font
        if(fontName in Text.fonts.keys()):
            return Text.fonts[key]

        if(fontFile):
            file_location = "{}".format(fontFile)
            font = pygame.font.Font(file_location, size)
        else:
            font = pygame.font.SysFont(fontName, size)

        key = fontName + "_" + str(size)

        Text.fonts[key] = font
        return font

    # Creates text element, takes a font and size as an argument
    def create(fontName, size, text, position, colour=(0, 0, 0), anti_alias=True, fontFile=None):

        font = Text.__loadFont(fontName, size, fontFile)
        textObj = font.render(text, anti_alias, colour)
        rect = textObj.get_rect()
        renderobject = RenderObject(textObj, rect, text)
        renderobject.setPosition(position)
        return renderobject