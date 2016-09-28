from constants import FIELD_H_NODES, FIELD_W_NODES


class Playground:
    def __init__(self):
        self.minx = 0
        self.maxx = FIELD_W_NODES - 1
        self.miny = 0
        self.maxy = FIELD_H_NODES - 1

playground = Playground()
