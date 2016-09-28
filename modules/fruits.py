import os.path
from random import choice, randint

from pygame import PixelArray, Surface
from pygame.locals import SRCALPHA

from __main__ import get_resource
from constants import NODE_H, NODE_W, PIC_DIR
from internal_events import InternalEvent
from libs.olbmp import OLBitMap
from modules.game import playground


APPLE_PIC = get_resource(os.path.join(PIC_DIR, "fruit_apple.olbmp"))
APRICOT_PIC = get_resource(os.path.join(PIC_DIR, "fruit_apricot.olbmp"))
CHERRY_PIC = get_resource(os.path.join(PIC_DIR, "fruit_cherry.olbmp"))
KIWI_PIC = get_resource(os.path.join(PIC_DIR, "fruit_kiwi.olbmp"))
PEAR_PIC = get_resource(os.path.join(PIC_DIR, "fruit_pear.olbmp"))
STRAWBERRY_PIC = get_resource(os.path.join(PIC_DIR, "fruit_strawberry.olbmp"))

app_ = None
images = {}
fruit_classes = []
fruits = []


def load_resources():
    images['apple'] = OLBitMap(APPLE_PIC)
    images['apricot'] = OLBitMap(APRICOT_PIC)
    images['cherry'] = OLBitMap(CHERRY_PIC)
    images['kiwi'] = OLBitMap(KIWI_PIC)
    images['pear'] = OLBitMap(PEAR_PIC)
    images['strawberry'] = OLBitMap(STRAWBERRY_PIC)


class FruitMeta(type):
    def __init__(cls, name, bases, namespace):
        super().__init__(name, bases, namespace)

        if namespace.get('abstract', False):
            del cls.abstract
            return

        fruit_classes.append(cls)


class Fruit(metaclass=FruitMeta):
    image_id = None
    increments = 1

    abstract = True

    def __init__(self, x, y):
        self._surface = Surface((NODE_W, NODE_H), SRCALPHA)
        self._image = images[self.image_id]
        self.x = x
        self.y = y

    def draw(self, dest):
        dest.blit(self._surface, (self.x * NODE_W, self.y * NODE_H))

    def render(self):
        pix_arr = PixelArray(self._surface)

        for i in range(NODE_H):
            for j in range(NODE_W):
                pix_arr[j, i] = self._image[j, i]

        del pix_arr


class Apple(Fruit):
    image_id = 'apple'


class Apricot(Fruit):
    image_id = 'apricot'


class Cherry(Fruit):
    image_id = 'cherry'


class Kiwi(Fruit):
    image_id = 'kiwi'


class Pear(Fruit):
    image_id = 'pear'


class Strawberry(Fruit):
    image_id = 'strawberry'


@InternalEvent('load')
def on_load(app):
    global app_
    app_ = app
    load_resources()


def spawn_fruit():
    x = randint(playground.minx, playground.maxx)
    y = randint(playground.miny, playground.maxy)

    fruit_class = choice(fruit_classes)

    fruit = fruit_class(x, y)
    fruit.render()

    fruits.append(fruit)

    app_.register_drawer('fruit', fruit.draw)


@InternalEvent('snake_step')
def on_snake_step(snake):
    for fruit in list(fruits):
        if (fruit.x, fruit.y) == (snake.x, snake.y):
            if fruit.increments > 0:
                for i in range(fruit.increments):
                    snake.increment()
            else:
                for i in range(abs(fruit.increments)):
                    snake.decrement()

            snake.render()

            InternalEvent.fire('fruit_eaten', fruit=fruit)


@InternalEvent('fruit_eaten')
def on_fruit_eaten(fruit):
    app_.unregister_drawer('fruit', fruit.draw)
    fruits.remove(fruit)

    spawn_fruit()


@InternalEvent('game_start')
def on_game_start():
    spawn_fruit()


@InternalEvent('game_end')
def on_game_end():
    for fruit in fruits:
        app_.unregister_drawer('fruit', fruit.draw)

    fruits[:] = []
