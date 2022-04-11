import traceback
import pygame, math, threading, sys, os
from sylia.renderobject import RenderObject
from sylia.shapes import Shape
from sylia.image import Image
from sylia.text import Text
from sylia.duck import Duck
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
            if not (('import' in line and 'sylia' in line) or 'sylia.init' in line):
                lines.append(line)

        commands = "\n".join(lines)

        try:
            exec(commands, globals(), globals())
        except SyntaxError as e:
            error_class = e.__class__.__name__
            detail = e.args[0]
            line_num =  e.lineno
            Sylia._running = False
        except Exception as e:
            error_class = e.__class__.__name__
            detail = e.args[0]
            _, __, exception_traceback = sys.exc_info()
            line_num =  traceback.extract_tb(exception_traceback)[-1][1]
            Sylia._running = False
        else:
            exec("sys.exit(0)")
            return
        raise Exception("{} at line {} of gamethread: {}".format(error_class, line_num, detail))

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

def init(screenSize, title="Sylia App", icon=None):
    if(icon == None):
        dirname = os.path.dirname(__file__)
        icon = dirname + '\sylia.png'
    
    image = pygame.image.load(icon)
    w = image.get_width()
    h = image.get_height()

    if(w != h or not isPower2(w)):
        raise Exception("Error: icon image must have equal dimensions that are a power of 2! ie 32x32, 64*64, 128x128, 256x256 ect...")
    Sylia.init(screenSize, title, image)

def running():
    sylia.clock.delay()
    return Sylia._running

def setBackgroundColour(colour):
    Sylia.background_colour = colour

def screenWidth():
    return Sylia.width

def screenHeight():
    return Sylia.height

def screenCenter():
    return [Sylia.width/2, Sylia.height/2]

def draw(drawable):

    if(isinstance(drawable, (Shape.Rectangle, Shape.Triangle, Shape.Circle))):
        renderobject = drawable.renderObject
    else:
        renderobject = drawable

    Sylia.drawLock.acquire()
    if(renderobject.id not in Sylia.draw_list.keys()):
        Sylia.draw_list[renderobject.id] = renderobject
    Sylia.drawLock.release()


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
    setBackgroundColour = setBackgroundColour
    screenWidth = screenWidth
    screenHeight = screenHeight
    screenCenter = screenCenter
    draw = draw