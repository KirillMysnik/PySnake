from pygame import Color, Surface
from pygame.font import SysFont
from pygame.locals import (
    K_ESCAPE, KEYDOWN, MOUSEBUTTONDOWN, MOUSEBUTTONUP, SRCALPHA)

from constants import HEIGHT, WIDTH
from internal_events import InternalEvent


MENU_COLOR = (255, 255, 255, 100)
BUTTON_COLOR = (253, 40, 40)
BUTTON_CAPTION_COLOR = (255, 255, 255)
BUTTON_WIDTH = 400
BUTTON_HEIGHT = 100
LABEL_COLOR = (0, 0, 0)
CREATED_BY_LABEL_X = 10
CREATED_BY_LABEL_Y = HEIGHT - 15

app_ = None
menu = None
resume_button = None
start_button = None
clickables = []
_mouse_button_down_coords = None
_made_by_label = None
paused = False
finished = True


class Menu:
    def __init__(self):
        self._surface = Surface((WIDTH, HEIGHT), SRCALPHA)

    def render(self):
        self._surface.fill(MENU_COLOR)

    def draw(self, dest):
        dest.blit(self._surface, (0, 0))


class Button:
    def __init__(self, x, y, width, height, caption, text_size, color,
                 caption_color, caption_bold=False, caption_italic=False):

        self.clickable = False
        self.x = x
        self.y = y
        self.caption = caption
        self.text_size = text_size
        self.color = color
        self.caption_color = caption_color
        self.caption_bold = caption_bold
        self.caption_italic = caption_italic

        self._surface = Surface((width, height))

        clickables.append(self)

    def render(self):
        self._surface.fill(self.color)

        font = SysFont("Courier New", self.text_size,
                       bold=self.caption_bold, italic=self.caption_italic)

        text = font.render(self.caption, True, Color(*self.caption_color))

        w, h = self._surface.get_size()
        tw, th = text.get_size()
        x = max(0, w // 2 - tw // 2)
        y = max(0, h // 2 - th // 2)
        self._surface.blit(text, (x, y))

    def draw(self, dest):
        dest.blit(self._surface, (self.x, self.y))

    def check_coords(self, pos):
        if not self.clickable:
            return False

        x, y = pos
        x1, y1 = self.x, self.y
        w, h = self._surface.get_size()
        return (x1 <= x <= x1 + w) and (y1 <= y <= y1 + h)

    def click(self):
        raise NotImplementedError


class TextLabel:
    def __init__(self, x, y, caption, text_size, color, caption_bold=False,
                 caption_italic=False):

        self.x = x
        self.y = y
        self.text_size = text_size
        self.color = color
        self.caption = caption
        self.caption_bold = caption_bold
        self.caption_italic = caption_italic

        self._surface = None

    def render(self):
        font = SysFont("Courier New", self.text_size,
                       bold=self.caption_bold, italic=self.caption_italic)

        text = font.render(self.caption, True, Color(*self.color))
        self._surface = text

    def draw(self, dest):
        dest.blit(self._surface, (self.x, self.y))


class StartButton(Button):
    def click(self):
        InternalEvent.fire('game_start')


class ResumeButton(Button):
    def click(self):
        InternalEvent.fire('game_resume')


def on_mouse_button_down(e):
    global _mouse_button_down_coords
    _mouse_button_down_coords = e.pos


def on_mouse_button_up(e):
    global _mouse_button_down_coords
    for clickable in clickables:
        if clickable.check_coords(e.pos) and clickable.check_coords(
                _mouse_button_down_coords):

            clickable.click()

    _mouse_button_down_coords = None


def on_key_down(e):
    if finished:
        return

    global paused
    if e.key == K_ESCAPE:
        if paused:
            InternalEvent.fire('game_resume')
        else:
            InternalEvent.fire('game_pause')


def show_start_gui():
    app_.register_event_handler(MOUSEBUTTONDOWN, on_mouse_button_down)
    app_.register_event_handler(MOUSEBUTTONUP, on_mouse_button_up)
    app_.register_drawer('menu', menu.draw)
    app_.register_drawer('gui', start_button.draw)
    start_button.clickable = True


def hide_start_gui():
    app_.unregister_event_handler(MOUSEBUTTONDOWN, on_mouse_button_down)
    app_.unregister_event_handler(MOUSEBUTTONUP, on_mouse_button_up)
    app_.unregister_drawer('menu', menu.draw)
    app_.unregister_drawer('gui', start_button.draw)
    start_button.clickable = False


def show_pause_gui():
    app_.register_event_handler(MOUSEBUTTONDOWN, on_mouse_button_down)
    app_.register_event_handler(MOUSEBUTTONUP, on_mouse_button_up)
    app_.register_drawer('menu', menu.draw)
    app_.register_drawer('gui', resume_button.draw)
    resume_button.clickable = True


def hide_pause_gui():
    app_.unregister_event_handler(MOUSEBUTTONDOWN, on_mouse_button_down)
    app_.unregister_event_handler(MOUSEBUTTONUP, on_mouse_button_up)
    app_.unregister_drawer('menu', menu.draw)
    app_.unregister_drawer('gui', resume_button.draw)
    resume_button.clickable = False


@InternalEvent('load')
def on_load(app):
    global app_, _made_by_label, menu, resume_button, start_button
    app_ = app

    menu = Menu()
    menu.render()

    start_button = StartButton(
        WIDTH // 2 - BUTTON_WIDTH // 2,
        HEIGHT // 2 - BUTTON_HEIGHT // 2,
        BUTTON_WIDTH,
        BUTTON_HEIGHT,
        "START",
        48,
        BUTTON_COLOR,
        BUTTON_CAPTION_COLOR
    )
    start_button.render()

    resume_button = ResumeButton(
        WIDTH // 2 - BUTTON_WIDTH // 2,
        HEIGHT // 2 - BUTTON_HEIGHT // 2,
        BUTTON_WIDTH,
        BUTTON_HEIGHT,
        "RESUME",
        48,
        BUTTON_COLOR,
        BUTTON_CAPTION_COLOR
    )
    resume_button.render()

    _made_by_label = TextLabel(
        CREATED_BY_LABEL_X, CREATED_BY_LABEL_Y, "Created by Kirill Mysnik",
        12, LABEL_COLOR)

    _made_by_label.render()

    app_.register_drawer('gui', _made_by_label.draw)
    app_.register_event_handler(KEYDOWN, on_key_down)

    show_start_gui()


@InternalEvent('game_start')
def on_game_start():
    global finished
    finished = False
    hide_start_gui()


@InternalEvent('game_end')
def on_game_end():
    global finished
    finished = True
    show_start_gui()


@InternalEvent('game_pause')
def on_game_pause():
    global paused
    paused = True
    show_pause_gui()


@InternalEvent('game_resume')
def on_game_resume():
    global paused
    paused = False
    hide_pause_gui()
