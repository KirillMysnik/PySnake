import os
os.environ['SDL_VIDEO_CENTERED'] = '1'
import sys

import pygame
from pygame.display import set_caption, set_icon
from pygame.locals import *
pygame.init()

from constants import HEIGHT, TICKRATE, WIDTH
from internal_events import InternalEvent


__version__ = "1.0"
__author__ = "Kirill Mysnik"

sys.stderr = open('stderr.log', 'w')
sys.stdout = open('stdout.log', 'w')

WINDOW_TITLE = "PySnake v{} by {}".format(__version__, __author__)
RESOLUTION =  WIDTH, HEIGHT
BG_COLOR = pygame.Color('#FFFFFF')

render_order = []


def get_resource(path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, path)
    return path


with open(get_resource(os.path.join("resource", "render.txt"))) as f:
    for line in f:
        line = line.strip()
        if not line:
            continue

        render_order.append(line)


class MainApp:
    def __init__(self, argv):
        self._fullscreen = False
        self._screen = pygame.display.set_mode(RESOLUTION)
        self._clock = pygame.time.Clock()
        self._running = False

        self._event_handlers = {}
        self._event_proxies = []
        self._tick_listeners = []
        self._drawers = []

    def register_event_handler(self, e_type, handler):
        if e_type not in self._event_handlers:
            self._event_handlers[e_type] = []

        if handler in self._event_handlers[e_type]:
            raise ValueError("Handler is already registered")

        self._event_handlers[e_type].append(handler)

    def unregister_event_handler(self, e_type, handler):
        self._event_handlers[e_type].remove(handler)
        if not self._event_handlers[e_type]:
            del self._event_handlers[e_type]

    def register_event_proxy(self, handler):
        if handler in self._event_handlers:
            raise ValueError("Proxy is already registered")

        self._event_proxies.append(handler)

    def unregister_event_proxy(self, handler):
        self._event_proxies.remove(handler)

    def register_tick_listener(self, listener):
        if listener in self._tick_listeners:
            raise ValueError("Listener is already registered")

        self._tick_listeners.append(listener)

    def unregister_tick_listener(self, listener):
        self._tick_listeners.remove(listener)

    def register_drawer(self, id_, drawer):
        if (id_, drawer) in self._drawers:
            raise ValueError("Drawer is already registered")

        self._drawers.append((id_, drawer))
        self._drawers.sort(key=lambda item: render_order.index(item[0]))

    def unregister_drawer(self, id_, drawer):
        self._drawers.remove((id_, drawer))

    def toggle_fullscreen(self, state=None):
        fullscreen = not self._fullscreen if state is None else state
        if fullscreen:
            self._screen = pygame.display.set_mode(RESOLUTION, FULLSCREEN)

        else:
            self._screen = pygame.display.set_mode(RESOLUTION)

        self._fullscreen = fullscreen

    def quit(self):
        self._running = False

    def loop(self):
        self._running = True

        while self._running:
            self._clock.tick(TICKRATE)

            for e in pygame.event.get():
                if e.type == QUIT:
                    self._running = False

                elif (e.type is KEYDOWN and e.key == K_RETURN and
                              (e.mod & (KMOD_LALT | KMOD_RALT)) != 0):

                    self.toggle_fullscreen()

                # Call event-specific handlers
                for handler in self._event_handlers.get(e.type, ()):
                    handler(e)

                # Pass event to event proxies
                for proxy in self._event_proxies:
                    proxy(e)

            for listener in self._tick_listeners:
                listener()

            self._screen.fill(BG_COLOR)

            for id_, drawer in self._drawers:
                drawer(self._screen)

            pygame.display.update()


def main(argv):
    set_caption(WINDOW_TITLE)

    print("Initializing application...")
    app = MainApp(argv)

    print("Loading modules...")
    import modules
    print("All modules loaded.")

    InternalEvent.fire('load', app=app)

    print("Entering main loop...")
    app.loop()


if __name__ == "__main__":
    main(sys.argv[1:])
