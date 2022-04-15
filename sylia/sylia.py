import pygame, math, threading, sys, os
from sylia.renderobject import RenderObject
from sylia.shape import Shape
from sylia.image import Image
from sylia.text import Text
from copy import deepcopy
pygame.init()

class Sylia:

    _running = True
    surface = None
    width = None
    height = None
    clock = None
    renderclock = None
    background_colour = (0, 0, 0)
    framerate = 60 # there are two different framerates to stop flickering
    renderrate = framerate/2 # a framerate of 30
    draw_list = {}
    drawLock = threading.Lock()
    title = None
    icon = None

    class SThread(threading.Thread):
        def __init__(self, threadID, name, func):
            threading.Thread.__init__(self)
            self.threadID = threadID
            self.name = name
            self.func = func
        
        def run(self):
            self.func()

    def init(screenSize, title, icon):
        Sylia.title = title
        Sylia.icon = icon

        Sylia.clock = pygame.time.Clock()
        Sylia.renderclock = pygame.time.Clock()
        Sylia.width = screenSize[0]
        Sylia.height = screenSize[1]
        Sylia.surface = pygame.display.set_mode(screenSize)
        pygame.display.set_caption(Sylia.title, Sylia.title)
        pygame.display.set_icon(Sylia.icon)

        # Init RenderObject
        RenderObject.init(Sylia.surface)

        # Init Shapes
        Shape.init(Sylia.surface, Sylia.drawLock, Sylia.draw_list)

        # Init Images
        Image.init(Sylia.surface, Sylia.drawLock, Sylia.draw_list)

        # Init Text
        Text.init(Sylia.surface, Sylia.drawLock, Sylia.draw_list)

        # Init Duck
        Duck.init(Sylia.surface, [Sylia.width/2, Sylia.height/2], Sylia._running)

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
        Sylia.surface.fill(Sylia.background_colour)

        Sylia.drawLock.acquire()
        for renderobject in Sylia.draw_list.values():
            renderobject.render()
        Sylia.drawLock.release()

        Sylia.draw_list.clear()
            
        Duck.update()

        Sylia.renderclock.tick(Sylia.renderrate)

    def load_commands():
        file = sys.argv[0]
        f = open(file, "r")

        lines = []

        for line in f:
            if not ('sylia.init' in line):
                lines.append(line)
            else:
                lines.append("\n")

        #This now seems to work... reporting the correct error lines... for now
        if(not os.path.exists('__pycache__')):
            os.mkdir('__pycache__')

        with open('__pycache__/file.py', 'w') as FILE:
            FILE.writelines(lines)
        
        with open('__pycache__/file.py', 'r') as FILE:
            exec(FILE.read(), globals(), globals())

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

class Screen:
    def width():
        return Sylia.width

    def height():
        return Sylia.height

    def center():
        return [Sylia.width/2, Sylia.height/2]

    def colour(colour):
        Sylia.background_colour = colour

    def draw(drawable):
        if(isinstance(drawable, (Shape.Rectangle, Shape.Triangle, Shape.Circle))):
            renderobject = drawable.renderObject
        else:
            renderobject = drawable

        Sylia.drawLock.acquire()
        if(renderobject.id not in Sylia.draw_list.keys()):
            Sylia.draw_list[renderobject.id] = renderobject
        Sylia.drawLock.release()

class Duck:

    start_position = None
    position = None
    sprite = None #pygame.image.load("Resources\Images\yellow_ducky.png")
    rect = None
    eyes = None
    nose = None
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
        Duck.start_position = list(position)
        Duck.running = running
        Duck.rect = Shape.rectangle(list(Duck.position), [50, 50], (255, 255, 0))
        Duck.nose = Shape.rectangle(list(Duck.position), [0, 10], (255, 150, 0))
        Duck.nose.setExtended('right', 25)

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
                Duck.nose.setPosition(list(Duck.position))

                if(Duck.index >= abs(Duck.target[2])):
                    Duck.current_command = None
                    Duck.position[0] = Duck.target[0]
                    Duck.position[1] = Duck.target[1]

            elif(Duck.current_command.type == "turn"):

                Duck.angle += Duck.target[1]*Duck.speed
                Duck.index += Duck.speed

                Duck.rect.setRotation(Duck.angle)
                Duck.nose.setRotation(Duck.angle)

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
                    Screen.draw(Duck.rect)
                    Screen.draw(Duck.nose)
                    
    def getPosX():
        return Duck.position[0]

    def getPosY():
        return Duck.position[1]

    def reset():
        Duck.position = list(Duck.start_position)

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

class Clock:

    def framerate(fps):
        Sylia.setFramerate(fps)

    def delay():
        Sylia.clock.tick(Sylia.framerate)


class Sound:
    max_channels = 16
    pygame.mixer.set_num_channels(16)

    def load(soundfile):
        file_location = "{}".format(soundfile)
        return pygame.mixer.Sound(file_location)

    def stop(channel_number):
        channel = pygame.mixer.Channel(channel_number)
        channel.stop()

    def stopAll():
        for i in range(Sound.max_channels):
            channel = pygame.mixer.Channel(i)
            channel.stop()

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

def isPower2(n):
    return (n != 0) and (n & (n-1) == 0)

def init(screenSize=[800, 600], title="Sylia App", icon=None):
    if(icon == None):
        dirname = os.path.dirname(__file__)
        icon = os.path.join(dirname, 'sylia.png')
    
    image = pygame.image.load(icon)
    w = image.get_width()
    h = image.get_height()

    if(w != h or not isPower2(w)):
        raise Exception("Error: icon image must have equal dimensions that are a power of 2! ie 32x32, 64*64, 128x128, 256x256 ect...")
    Sylia.init(screenSize, title, image)

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
    screen = Screen
    running = running
    init = init