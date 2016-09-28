import os.path

from pygame import PixelArray, Surface
from pygame.locals import K_DOWN, K_LEFT, K_RIGHT, K_UP, KEYDOWN, SRCALPHA

from __main__ import get_resource
from constants import NODE_H, NODE_W, PIC_DIR
from internal_events import InternalEvent
from libs.olbmp import OLBitMap
from modules.game import playground


SNAKE_PIC = get_resource(os.path.join(PIC_DIR, "snake.olbmp"))
MIN_SPEED = 0.125
DEFAULT_SPEED = MIN_SPEED * 2
DISP_PRECISION = 0
INIT_X = 20
INIT_Y = 10
INIT_LENGTH = 3
BORDER_COLOR = (0, 0, 0, 255)
DRAW_BORDER = False

app_ = None
snake_image = None
snake = None


def load_resources():
    global snake_image
    snake_image = OLBitMap(SNAKE_PIC)


class Direction:
    NONE = 0
    UP = 1
    RIGHT = 2
    DOWN = 3
    LEFT = 4


class SnakeNode:
    def __init__(self, offset_x, offset_y):
        self.x = offset_x
        self.y = offset_y
        self._surface = Surface((NODE_W, NODE_H), SRCALPHA)

    def draw(self, dest, offset_x, offset_y):
        dest.blit(self._surface, (NODE_W * offset_x, NODE_H * offset_y))

    def render(self, next_node):
        pix_arr = PixelArray(self._surface)

        for i in range(NODE_H):
            for j in range(NODE_W):
                pix_arr[j, i] = snake_image[j, i]

        if DRAW_BORDER:
            # Top border
            if self.y != 1 and ((not next_node) or next_node.y != -1):
                for j in range(NODE_W):
                    pix_arr[j, 0] = BORDER_COLOR

            # Right border
            if self.x != -1 and ((not next_node) or next_node.x != 1):
                for i in range(NODE_H):
                    pix_arr[NODE_W - 1, i] = BORDER_COLOR

            # Bottom border
            if self.y != -1 and ((not next_node) or next_node.y != 1):
                for j in range(NODE_W):
                    pix_arr[j, NODE_H - 1] = BORDER_COLOR

            # Left border
            if self.x != 1 and ((not next_node) or next_node.x != -1):
                for i in range(NODE_H):
                    pix_arr[0, i] = BORDER_COLOR

        del pix_arr


class Snake(list):
    def __init__(self, x, y):
        super().__init__()

        self.active = True
        self.x = x
        self.y = y
        self._direction = Direction.RIGHT
        self._speed = DEFAULT_SPEED
        self._surface = Surface((NODE_W, NODE_H), SRCALPHA)

        self.next_direction = Direction.RIGHT

    def get_speed(self):
        return self._speed

    def set_speed(self, speed):
        self._speed = max(MIN_SPEED, speed)

    speed = property(get_speed, set_speed)

    def check_collision(self):
        if not self:
            return False

        # Self-collision
        x, y = self.x, self.y
        for node in self[1:]:
            x += node.x
            y += node.y

            if x == self.x and y == self.y:
                return True

        # Collision with the field
        x, y = self.x, self.y
        if x < playground.minx or x > playground.maxx:
            return True

        if y < playground.miny or y > playground.maxy:
            return True

        return False

    def draw(self, dest):
        x, y = int(self.x), int(self.y)
        if self._direction == Direction.DOWN:
            if self.y - y > DISP_PRECISION:
                y += 1

        elif self._direction == Direction.RIGHT:
            if self.x - x > DISP_PRECISION:
                x += 1

        for node in self:
            x += node.x
            y += node.y

            node.draw(dest, x, y)

    def render(self):
        for i in range(len(self)):
            if i + 1 < len(self):
                next_node = self[i + 1]
            else:
                next_node = None

            self[i].render(next_node)

    def increment(self):
        if not self:
            x, y = 0, 0
        else:
            x, y = self[-1].x, self[-1].y
            if (x, y) == (0, 0):
                x, y = -1, 0

        self.append(SnakeNode(x, y))

    def decrement(self):
        if not self:
            raise ValueError("Empty snake!")

        self.pop()

    def tick(self):
        if not self.active:
            return

        # Turn handling
        if (
                self.y - int(self.y) <= DISP_PRECISION and
                self.x - int(self.x) <= DISP_PRECISION):

            self._direction = self.next_direction

            # Collision check
            if self.check_collision():
                self.active = False
                InternalEvent.fire('game_end')
                return

            for i in range(len(self) - 1, 0, -1):
                self[i].x = self[i - 1].x
                self[i].y = self[i - 1].y

                if (self[i].x, self[i].y) == (0, 0):
                    self[i].x = {
                        Direction.RIGHT: -1,
                        Direction.LEFT: 1,
                    }.get(self._direction, 0)

                    self[i].y = {
                        Direction.UP: 1,
                        Direction.DOWN: -1,
                    }.get(self._direction, 0)

            InternalEvent.fire('snake_step', snake=self)

            if DRAW_BORDER:
                self.render()

        # Displacement
        if self._direction == Direction.UP:
            self.y -= self._speed

        elif self._direction == Direction.RIGHT:
            self.x += self._speed

        elif self._direction == Direction.DOWN:
            self.y += self._speed

        elif self._direction == Direction.LEFT:
            self.x -= self._speed

    def on_key_down(self, e):
        if e.key == K_UP:
            if self._direction in (Direction.RIGHT, Direction.LEFT):
                self.next_direction = Direction.UP
        elif e.key == K_RIGHT:
            if self._direction in (Direction.UP, Direction.DOWN):
                self.next_direction = Direction.RIGHT
        elif e.key == K_DOWN:
            if self._direction in (Direction.RIGHT, Direction.LEFT):
                self.next_direction = Direction.DOWN
        elif e.key == K_LEFT:
            if self._direction in (Direction.UP, Direction.DOWN):
                self.next_direction = Direction.LEFT


@InternalEvent('load')
def on_load(app):
    global app_
    app_ = app
    load_resources()


@InternalEvent('game_start')
def on_game_start():
    global snake
    if snake is not None:
        app_.unregister_drawer('snake', snake.draw)
        app_.unregister_tick_listener(snake.tick)
        app_.unregister_event_handler(KEYDOWN, snake.on_key_down)

    snake = Snake(INIT_X, INIT_Y)
    for i in range(INIT_LENGTH):
        snake.increment()

    snake.render()
    app_.register_drawer('snake', snake.draw)
    app_.register_tick_listener(snake.tick)
    app_.register_event_handler(KEYDOWN, snake.on_key_down)


@InternalEvent('game_pause')
def on_game_pause():
    snake.active = False


@InternalEvent('game_resume')
def on_game_resume():
    snake.active = True
