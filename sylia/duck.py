import pygame
import threading
import math
import sys
from copy import deepcopy
from sylia.shapes import Shape

class Duck:

    start_position = None
    position = None
    sprite = None #pygame.image.load("Resources\Images\yellow_ducky.png")
    rect = None
    visible = False
    angle = 0
    speed = 5
    size = 1
    width = 1
    trace = True
    icon = True
    commands = []
    command_running = False
    current_command = None
    target = None
    index = 0
    threadLock = threading.Lock()
    syncLock = threading.Lock()
    points = []
    surface = None
    running = None

    class Point():
        def __init__(self, position, colour="black", width="1"):
            self.position = position
            self.colour = colour
            self.width = width

    class Command():
        def __init__(self, type, args):
            self.type = type
            self.args = args


    def init(surface, position, running):
        Duck.surface = surface
        Duck.position = position
        Duck.start_position = position
        Duck.running = running
        Duck.rect = Shape.rectangle(list(Duck.position), [50, 50], (255, 255, 0))

    """Internally called each tick to update the duck"""
    def update():

        # If no command is running get a new command
        if(Duck.current_command == None and len(Duck.commands) > 0):
            
            if(Duck.syncLock.locked()):
                Duck.syncLock.release()

            Duck.index = 0
            Duck.target = None

            # Make sure that we are not trying to add a command while we are popping one
            Duck.threadLock.acquire
            Duck.current_command = Duck.commands.pop(0)
            Duck.threadLock.release
            
            # Set the target based on the command to know its complete
            if(Duck.current_command.type == "move"):
                target_x = Duck.position[0] + Duck.current_command.args*math.cos(math.radians(Duck.angle))
                target_y = Duck.position[1] - Duck.current_command.args*math.sin(math.radians(Duck.angle))
                Duck.target = (target_x, target_y, Duck.current_command.args)
                point = deepcopy(Duck.Point(Duck.position))
                Duck.points.append(point)

            if(Duck.current_command.type == "turn"):
                target_angle = Duck.angle + Duck.current_command.args
                
                if(Duck.current_command.args != 0):
                    sign = Duck.current_command.args / abs(Duck.current_command.args)
                else:
                    sign = 1
                Duck.target = (target_angle, sign, Duck.current_command.args)

        if(Duck.current_command != None):
            if(Duck.current_command.type == "move"):

                sign = Duck.current_command.args / abs(Duck.current_command.args)
                Duck.position[0] += sign*Duck.speed*math.cos(math.radians(Duck.angle))
                Duck.position[1] -= sign*Duck.speed*math.sin(math.radians(Duck.angle))
                Duck.index += Duck.speed

                Duck.rect.setPosition(list(Duck.position))

                if(Duck.index >= abs(Duck.target[2])):
                    Duck.current_command = None
                    Duck.position[0] = Duck.target[0]
                    Duck.position[1] = Duck.target[1]

            elif(Duck.current_command.type == "turn"):

                Duck.angle += Duck.target[1]*Duck.speed
                Duck.index += Duck.speed

                Duck.rect.setAngle(Duck.angle)

                if(Duck.index >= abs(Duck.target[2])):
                    Duck.current_command = None
                    Duck.angle = Duck.target[0]

        # Draw the duck
        if(Duck.visible):

            # Draw trail behind duck
            if(Duck.trace):
                for i in range(0, len(Duck.points)):
                    if(i+1 >= len(Duck.points)):
                        pygame.draw.line(Duck.surface, (0,255,0), Duck.points[i].position, Duck.position, width=Duck.width)
                    else:
                        pygame.draw.line(Duck.surface, (255,0,0), Duck.points[i].position, Duck.points[i+1].position, width=Duck.width)

            # Draw the duck
            if(Duck.icon):

                if(Duck.sprite):
                    sprite = pygame.transform.scale(Duck.sprite, (int(Duck.size*50), int(Duck.size*50)))
                    sprite = pygame.transform.rotate(sprite, Duck.angle)
                    rect = sprite.get_rect()
                    rect.center = (Duck.position[0], Duck.position[1])
                    Duck.surface.blit(sprite, rect)

                else:
                    Shape.draw(Duck.rect)
                    
    def getPosX():
        return Duck.position[0]

    def getPosY():
        return Duck.position[1]

    def reset():
        Duck.position = Duck.start_position

    """Add move to list of commands for duck to follow"""
    def move(distance):
        Duck.visible = True

        if(Duck.running != True):
            return

        passed = Duck.syncLock.acquire(timeout=5)
        if(not passed):
            sys.exit(0)

        # Make sure that nothing else changes the command list while adding commands
        Duck.threadLock.acquire()
        cmd = Duck.Command("move", distance)
        Duck.commands.append(cmd)
        Duck.threadLock.release()

        

    """Add turn to list of commands for duck to follow"""
    def turn(angle):
        Duck.visible = True

        if(Duck.running != True):
            return

        passed = Duck.syncLock.acquire(timeout=5)
        if(not passed):
            sys.exit(0)

        # Make sure that nothing else changes the command list while adding commands
        Duck.threadLock.acquire()
        cmd = Duck.Command("turn", angle)
        Duck.commands.append(cmd)
        Duck.threadLock.release()

    def image(filename):
        Duck.sprite = pygame.image.load("{}".format(filename))
        Duck.visible = True