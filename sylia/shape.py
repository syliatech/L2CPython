import pygame
import math
from sylia.renderobject import RenderObject

class Shape:

    surface = None
    drawLock = None
    drawList = None

    class Rectangle:
        def __init__(self, position, dimensions, colour):
            x = position[0]
            y = position[1]
            w = dimensions[0]/2
            h = dimensions[1]/2
            self.position = list(position)
            self.dimensions = dimensions
            self.scale = [1, 1] #Scale the shape in both directions
            self.extend = [0, 0, 0, 0] #Extend a particular face in that direction
            self.angle = 0
            self.colour = colour
            self.points = [[x-w,y-h], [x+w, y-h], [x+w, y+h], [x-w, y+h]]
            self.renderObject = RenderObject(self, None, 'primative-rectangle', True)

        # Used by rotate to create shape at (0, 0) prior to applying translation
        def build_zero_shape(self):
            x = 0
            y = 0
            w = self.dimensions[0]/2*self.scale[0]
            h = self.dimensions[1]/2*self.scale[1]

            # Take extended sides into account
            wl = -(w+self.extend[0])
            wr = w+self.extend[1]
            ht = -(h+self.extend[2])
            hb = h+self.extend[3]

            return [[x+wl,y+ht], [x+wr, y+ht], [x+wr, y+hb], [x+wl, y+hb]]

        # Used to apply position translation once rotation has occured
        def translate(self, points):
            for i in range(len(self.points)):
               points[i][0] += self.position[0]
               points[i][1] += self.position[1]

        def setPosition(self, position):
            position = list(position)
            self.position = position

        def setSize(self, dimensions):
            self.dimensions = dimensions

        def setExtended(self, side, amount):
            if(side == 'left'):
                self.extend[0] = amount
            elif(side == 'right'):
                self.extend[1] = amount
            elif(side == 'bottom'):
                self.extend[2] = amount
            elif(side == 'top'):
                self.extend[3] = amount
            else:
                raise Exception("Error: setExtend expects side argument for rectangle to be: 'left', 'right', 'top' or 'bottom'. {} is not a side".format(side))

        def setRotation(self, angle):
            self.angle = -math.radians(angle)

        def __handle_transforms(self):
            zpoints = self.build_zero_shape()

            for i in range(len(self.points)):
                x1 = zpoints[i][0]
                y1 = zpoints[i][1]
                zpoints[i][0] = (math.cos(self.angle)*x1) + (math.sin(self.angle)*y1)
                zpoints[i][1] = (math.sin(self.angle)*x1) - (math.cos(self.angle)*y1)

            self.translate(zpoints)
            self.points = list(zpoints)

        def setColour(self, colour):
            self.colour = colour

        def draw(self):
            self.__handle_transforms()
            pygame.draw.polygon(Shape.surface, self.colour, self.points)

    class Circle:
        def __init__(self, position, diameter, colour):
            self.position = list(position)
            self.colour = colour
            self.diameter = diameter
            self.renderObject = RenderObject(self, None, 'primative-circle', True)

        def setDiameter(self, diameter):
            self.diameter = diameter

        def setPosition(self, position):
            self.position = list(position)

        def setColour(self, colour):
            self.colour = colour

        def draw(self):
            pygame.draw.circle(Shape.surface, self.colour, self.position, radius=self.diameter/2)

    class Triangle(Rectangle):
        def __init__(self, position, size, colour):
            self.position = position
            self.radius = size
            self.colour = colour
            self.extend = [0, 0, 0]
            self.scale = 1
            self.angle = 0
            self.renderObject = RenderObject(self, None, 'primative-circle', True)

            r = size
            x = position[0]
            y = position[1]
            rx1 = r*math.cos(math.radians(210))
            ry1 = r*math.sin(math.radians(210))
            rx2 = r*math.cos(math.radians(330))
            ry2 = r*math.sin(math.radians(330))                 
            self.points = [[x, y+r], [x+rx1, y+ry1], [x+rx2, y+ry2]]

        def build_zero_shape(self):
            r = self.radius
            x = 0
            y = 0

            ext = self.extend[0]
            exl = self.extend[1]
            exr = self.extend[2]

            rx1 = (r+exl)*math.cos(math.radians(210))
            ry1 = (r+exl)*math.sin(math.radians(210))
            rx2 = (r+exr)*math.cos(math.radians(330))
            ry2 = (r+exr)*math.sin(math.radians(330))

            return [[x, y+r+ext], [x+rx1, y+ry1], [x+rx2, y+ry2]]

        def setSize(self, size):
            self.radius = size

        def setExtended(self, side, amount):
            if(side == "top"):
                self.extend[0] = amount
            elif(side == "left"):
                self.extend[1] = amount
            elif(side == "right"):
                self.extend[2] = amount
            else:
                raise Exception("Error: setExtend expects side argument for rectangle to be: 'left', 'right' or 'top'. {} is not a side".format(side))

        def setColour(self, colour):
            self.colour = colour

    # This is called internally
    def init(surface, drawLock, drawList):
        Shape.surface = surface
        Shape.drawLock = drawLock
        Shape.drawList = drawList

    def rectangle(position, dimensions, colour):
        rect = Shape.Rectangle(position, dimensions, colour)
        return rect

    def circle(position, diameter, colour):
        round_thing = Shape.Circle(position, diameter, colour)
        return round_thing

    def triangle(position, radius, colour):
        pointy_thing = Shape.Triangle(position, radius, colour)
        return pointy_thing