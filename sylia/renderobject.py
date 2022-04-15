import pygame

class RenderObject:

    id = 0
    surface = None

    def init(surface):
        RenderObject.surface = surface

    def __init__(self, image, rect, file, primative=False):
        self.file = file
        self.image = image
        self.rect = rect
        self.id = RenderObject.id
        self.angle = 0
        self.size = None
        self.primative = primative
        RenderObject.id += 1

    def setPosition(self, position):
        self.rect.center = position

    def setRotation(self, angle):
        self.angle = angle

    def setScale(self, size):
        try:
            if(len(size) != 2):
                raise Exception("Error: setScale expects an array with two elements [width, height]")
        except:
            raise Exception("Error: setScale expects an array with two elements [width, height]")
        self.size = size

    def render(self):
        # Check if we are dealing with a primative (ie a shape)
        if(self.primative):
            self.image.draw() #use the primative inbuilt draw() method instead
            return
        # Check if image is scaled (otherwise do not scale)  
        if(self.size):
            image = pygame.transform.scale(self.image, (int(self.rect.width*self.size[0]), int(self.rect.height*self.size[1])))
            image = pygame.transform.rotate(image, self.angle)
        else:
            image = pygame.transform.rotate(self.image, self.angle)
        rect = image.get_rect(center=self.rect.center)
        RenderObject.surface.blit(image, rect)
