import pygame, math, threading, sys
from copy import deepcopy
pygame.init()

class Sylia:

    _running = True
    surface = None
    width = 800
    height = 600
    clock = None
    renderclock = None
    framerate = 60 # there are two different framerates to stop flickering
    renderrate = framerate/2 # a framerate of 30
    draw_list = {}
    drawLock = threading.Lock()

    class SThread(threading.Thread):
        def __init__(self, threadID, name, func):
            threading.Thread.__init__(self)
            self.threadID = threadID
            self.name = name
            self.func = func
        
        def run(self):
            self.func()

    def init():
        Sylia.clock = pygame.time.Clock()
        Sylia.renderclock = pygame.time.Clock()
        windowsize = (Sylia.width, Sylia.height)
        Sylia.surface = pygame.display.set_mode(windowsize)
        Sylia.run()

    def setFramerate(framerate):
        Sylia.framerate = framerate*2
        Sylia.renderrate = framerate

    def events():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                Sylia._running = False
                if(Duck.syncLock.locked()):
                    Duck.syncLock.release()

            if event.type == pygame.KEYDOWN:
                key = pygame.key.name(event.key)
                Key.down(key)

            if event.type == pygame.KEYUP:
                key = pygame.key.name(event.key)
                Key.up(key)

            if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.MOUSEBUTTONUP:
                mouse_presses = pygame.mouse.get_pressed()
                if mouse_presses[0]:
                    Mouse.down("left")
                else:
                    Mouse.up("left")
                if mouse_presses[1]:
                    Mouse.down("middle")
                else:
                    Mouse.up("middle")
                if mouse_presses[2]:
                    Mouse.down("right")
                else:
                    Mouse.up("right")

    def loop():
        Sylia.events()
        pygame.display.update()
        Sylia.surface.fill((0,0,0))

        Sylia.drawLock.acquire()
        for renderobject in Sylia.draw_list.values():
            Image.__draw__(renderobject)
        Sylia.drawLock.release()

        Sylia.draw_list.clear()
            
        Duck.update()

        Sylia.renderclock.tick(Sylia.renderrate)

    def load_commands():
        file = sys.argv[0]
        f = open(file, "r")

        lines = []

        for line in f:
            if not (('import' in line and 'sylia' in line) or 'sylia.init' in line):
                lines.append(line)

        commands = "\n".join(lines)

        exec(commands)
        exec("sys.exit(0)")

    def run():
        game_thread = Sylia.SThread(1, "game_thread", Sylia.load_commands)
        game_thread.start()

        while(Sylia._running):
            Sylia.loop()

        Sylia.cleanup()

        game_thread.join()
        exec("sys.exit(0)") 


    def cleanup():
        if(Duck.syncLock.locked()):
            Duck.syncLock.release()

        pygame.quit()

class Clock:

    def framerate(fps):
        Sylia.setFramerate(fps)

    def delay():
        Sylia.clock.tick(Sylia.framerate)

class RenderObject:

    id = 0

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
        if(len(size) != 2):
            raise Exception("Error: size expects an array with two elements [width, height]")
        self.size = size

    def render(self):
        # Check if we are dealing with a primative (ie a shape)
        if(self.primative):
            self.image.draw() #use the primative inbuilt draw() method
            return
        # Check if image is scaled (otherwise do not scale)  
        if(self.size):
            self.image = pygame.transform.scale(self.image, (int(self.rect.width*self.size[0]), int(self.rect.height*self.size[1])))
        self.image = pygame.transform.rotate(self.image, self.angle)
        Sylia.surface.blit(self.image, self.rect)

class Shape:

    class Rectangle:
        def __init__(self, position, dimensions, colour):
            x = position[0]
            y = position[1]
            w = dimensions[0]/2
            h = dimensions[1]/2
            self.position = position
            self.dimensions = dimensions
            self.scale = [1, 1] #Scale the shape in both directions
            self.extend = [0, 0, 0, 0] #Extend a particular face in that direction
            self.angle = 0
            self.colour = colour
            self.points = [[x-w,y-h], [x+w, y-h], [x+w, y+h], [x-w, y+h]]
            self.renderObject = RenderObject(self, None, 'primative-rectangle', True)

        # Used by rotate to create shape at (0, 0) prior to applying translation
        def __build_zero_shape(self):
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
        def __translate(self, points):
            for i in range(len(self.points)):
               points[i][0] += self.position[0]
               points[i][1] += self.position[1]

        def setPosition(self, position):
           offset = [position[0] - self.position[0], self.position[1] - position[1]]
           self.position = position

           for i in range(len(self.points)):
               self.points[i][0] += offset[0]
               self.points[i][1] += offset[1]

        def setScale(self, dimensions):
            self.scale = [dimensions[0]/self.dimensions[0], dimensions[1]/self.dimensions[1]]
            self.dimensions = dimensions

            for i in range(len(self.points)):
                self.points[i][0] *= self.scale[0]
                self.points[i][1] *= self.scale[1]

        def setExtended(self, side, amount):
            if(side == 'left'):
                self.extend[0] = amount
            elif(side == 'right'):
                self.extend[1] = amount
            elif(side == 'top'):
                self.extend[2] = amount
            elif(side == 'bottom'):
                self.extend[3] = amount
            else:
                raise Exception("Error: setExtend expects side argument for rectangle to be: 'left', 'right', 'top' or 'bottom'. {} is not a side".format(side))

            #Update everything
            self.setAngle(self.angle)

        def setAngle(self, angle):
            self.angle = angle

            zpoints = self.__build_zero_shape()

            for i in range(len(self.points)):
                x1 = zpoints[i][0]
                y1 = zpoints[i][1]
                zpoints[i][0] = (math.cos(angle)*x1) - (math.sin(angle)*y1)
                zpoints[i][1] = (math.sin(angle)*x1) + (math.cos(angle)*y1)

            self.__translate(zpoints)
            self.points = list(zpoints)

        def draw(self):
            pygame.draw.polygon(Sylia.surface, self.colour, self.points)

    class Circle:
        def __init__(self, position, diameter, colour):
            self.position = position
            self.colour = colour
            self.diameter = diameter
            self.renderObject = RenderObject(self, None, 'primative-circle', True)

        def setDiameter(self, diameter):
            self.diameter = diameter

        def setPosition(self, position):
            self.position = position

        def draw(self):
            pygame.draw.circle(Sylia.surface, self.colour, self.position, radius=self.diameter/2)


    def rectangle(position, dimensions, colour):
        rect = Shape.Rectangle(position, dimensions, colour)
        return rect

    def circle(position, diameter, colour):
        round_thing = Shape.Circle(position, diameter, colour)
        return round_thing

    def polygon(points, colour):
        pygame.draw.polygon(Sylia.surface, colour, points=points)

        """Public draw function, adds to list for Sylia to draw"""
    def draw(primativeObject):
        renderobject = primativeObject.renderObject
        Sylia.drawLock.acquire()
        if(renderobject.id not in Sylia.draw_list.keys()):
            Sylia.draw_list[renderobject.id] = renderobject
        Sylia.drawLock.release()

class Text:
    
    fonts = {}

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
    def create(fontName, size, text, position, colour=(0, 0, 0), anti_alias=False, fontFile=None):

        font = Text.__loadFont(fontName, size, fontFile)
        textObj = font.render(text, anti_alias, colour)
        rect = textObj.get_rect()
        renderobject = RenderObject(textObj, rect, text)
        renderobject.setPosition(position)
        return renderobject

    """Actually handles the drawing of the image, called only internally by Sylia"""
    def __draw__(renderobject):
        renderobject.render()

    """Public draw function, adds to list for Sylia to draw"""
    def draw(renderobject):

        Sylia.drawLock.acquire()
        if(renderobject.id not in Sylia.draw_list.keys()):
            Sylia.draw_list[renderobject.id] = renderobject
        Sylia.drawLock.release()


class Image:

    def load(imgfile):
        file_location = "{}".format(imgfile)
        image = pygame.image.load(file_location)
        rect = image.get_rect()
        renderobject = RenderObject(image, rect, imgfile)
        return renderobject

    """Actually handles the drawing of the image, called only internally by Sylia"""
    def __draw__(renderobject):
        renderobject.render()

    """Public draw function, adds to list for Sylia to draw"""
    def draw(renderobject):

        Sylia.drawLock.acquire()
        if(renderobject.id not in Sylia.draw_list.keys()):
            Sylia.draw_list[renderobject.id] = renderobject
        Sylia.drawLock.release()

class Sound:
    pygame.mixer.set_num_channels(8)

    def load(soundfile):
        file_location = "{}".format(soundfile)
        return pygame.mixer.Sound(file_location)

    def play(sound, channel_number=1):
        channel = pygame.mixer.Channel(channel_number)

        if channel.get_busy():
            channel.stop()

        channel.play(sound)

class Key:
    keys = {}

    def up(keyname):
        Key.keys[keyname] = False

    def down(keyname):
        Key.keys[keyname] = True

    def pressed(keyname):
        if keyname not in Key.keys:
            return False

        if Key.keys[keyname]:
            return True
        else:
            return False

class Mouse:

    buttons = {}

    def up(button):
        Mouse.buttons[button] = False

    def down(button):
        Mouse.buttons[button] = True

    def pressed(button):
        if button not in Mouse.buttons:
            return False

        if Mouse.buttons[button]:
            return True
        else:
            return False

    def position():
        return pygame.mouse.get_pos()

class Duck:

    position = [Sylia.width/2, Sylia.height/2]
    sprite = None #pygame.image.load("Resources\Images\yellow_ducky.png")
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

    class Point():
        def __init__(self, position, colour="black", width="1"):
            self.position = position
            self.colour = colour
            self.width = width

    class Command():
        def __init__(self, type, args):
            self.type = type
            self.args = args

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

                if(Duck.index >= abs(Duck.target[2])):
                    Duck.current_command = None
                    Duck.position[0] = Duck.target[0]
                    Duck.position[1] = Duck.target[1]

            elif(Duck.current_command.type == "turn"):

                Duck.angle += Duck.target[1]*Duck.speed
                Duck.index += Duck.speed

                if(Duck.index >= abs(Duck.target[2])):
                    Duck.current_command = None
                    Duck.angle = Duck.target[0]

        # Draw the duck
        if(Duck.visible):

            # Draw trail behind duck
            if(Duck.trace):
                for i in range(0, len(Duck.points)):
                    if(i+1 >= len(Duck.points)):
                        pygame.draw.line(Sylia.surface, (0,255,0), Duck.points[i].position, Duck.position, width=Duck.width)
                    else:
                        pygame.draw.line(Sylia.surface, (255,0,0), Duck.points[i].position, Duck.points[i+1].position, width=Duck.width)

            # Draw the duck
            if(Duck.icon):

                if(Duck.sprite):
                    sprite = pygame.transform.scale(Duck.sprite, (int(Duck.size*50), int(Duck.size*50)))
                    sprite = pygame.transform.rotate(sprite, Duck.angle)
                    rect = sprite.get_rect()
                    rect.center = (Duck.position[0], Duck.position[1])
                    Sylia.surface.blit(sprite, rect)

                else:
                    Shape.rectangle([Duck.position[0] - Duck.size*25, Duck.position[1] - Duck.size*25], [Duck.size*50, Duck.size*50], (255, 255, 0))

    def getPosX():
        return Duck.position[0]

    def getPosY():
        return Duck.position[1]

    def reset():
        Duck.position = [Sylia.width/2, Sylia.height/2]

    """Add move to list of commands for duck to follow"""
    def move(distance):
        Duck.visible = True

        if(Sylia._running != True):
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

        if(Sylia._running != True):
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

def init():
    Sylia.init()

def running():
    sylia.clock.delay()
    return Sylia._running

#Dummy Class
class sylia:

    duck = Duck
    clock = Clock
    shape = Shape
    image = Image
    text = Text
    sound = Sound
    key = Key
    mouse = Mouse
    running = running