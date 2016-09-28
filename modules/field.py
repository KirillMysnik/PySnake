import os.path

from pygame import PixelArray, Surface
from pygame.locals import SRCALPHA

from __main__ import get_resource
from constants import FIELD_H_NODES, FIELD_W_NODES, NODE_H, NODE_W, PIC_DIR
from internal_events import InternalEvent
from libs.olbmp import OLBitMap


FIELD_PIC = get_resource(os.path.join(PIC_DIR, "field.olbmp"))
SHADOWS_PIC = get_resource(os.path.join(PIC_DIR, "shadows.olbmp"))
FIELD_W = FIELD_W_NODES * NODE_W
FIELD_H = FIELD_H_NODES * NODE_H
FIELD_COLOR = (0, 0, 0, 255)
DEBUG_GRID = False

field_image = None
shadows_image = None
field = None
shadows = None


def load_resources():
    global field_image, shadows_image
    field_image = OLBitMap(FIELD_PIC)
    shadows_image = OLBitMap(SHADOWS_PIC)


class AreaWideImage:
    def __init__(self, image):
        self._surface = Surface((FIELD_W, FIELD_H), SRCALPHA)
        self._image = image

    def render(self):
        pix_arr = PixelArray(self._surface)

        for i in range(FIELD_H):
            for j in range(FIELD_W):
                pix_arr[j, i] = self._image[j, i]

        if DEBUG_GRID:
            for node_i in range(FIELD_H_NODES):
                for node_j in range(FIELD_W_NODES):
                    for i in range(NODE_H):
                        pix_arr[
                            node_j * NODE_W, node_i * NODE_H + i] = FIELD_COLOR

                    for j in range(NODE_W):
                        pix_arr[
                            node_j * NODE_W + j, node_i * NODE_H] = FIELD_COLOR

        del pix_arr

    def draw(self, dest):
        dest.blit(self._surface, (0, 0))


@InternalEvent('load')
def on_load(app):
    load_resources()

    global field, shadows
    field = AreaWideImage(field_image)
    field.render()
    app.register_drawer('field', field.draw)
    shadows = AreaWideImage(shadows_image)
    shadows.render()
    app.register_drawer('shadows', shadows.draw)
