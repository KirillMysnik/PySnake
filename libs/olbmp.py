import os.path


INIT_COLOR = (255, 255, 255, 255)
VERSION = 1

# Don't change values below
MAX_WIDTH = 65535
MAX_HEIGHT = 65535


class CorruptedFile(Exception):
    pass


class OLBitMap:
    def __init__(self, source):
        if isinstance(source, OLBitMap):
            self._copy(source)
            return

        if hasattr(source, 'read'):
            self._load_bin_data(source.read())
            return

        if isinstance(source, bytes):
            self._load_bin_data(source)
            return

        if isinstance(source, str) and os.path.isfile(source):
            with open(source, 'rb') as f:
                self._load_bin_data(f.read())
                return

        if hasattr(source, '__iter__'):
            if len(source) != 2:
                raise ValueError("(width,height) tuple should be length of 2")

            width, height = source
            self._new(width, height)
            return

        raise TypeError(
            "source should be either file path, file-like "
            "object, OLBitMap instance, bytes or (width,height) tuple - "
            "'{}' instance found instead".format(type(source)))

    def _load_bin_data(self, bindata):
        if bindata[:5].decode('ascii') != 'OLBMP':
            raise IOError("Missing OLBMP header")

        self.version = bindata[5]
        self.width = bindata[6] * 256 + bindata[7]
        self.height = bindata[8] * 256 + bindata[9]

        self._bitmap = [[None, ] * self.width for i in range(self.height)]

        for i in range(self.height):
            for j in range(self.width):
                offset = 10 + i*self.width*4 + j*4
                r = bindata[offset + 0]
                g = bindata[offset + 1]
                b = bindata[offset + 2]
                a = bindata[offset + 3]

                self._bitmap[i][j] = (r, g, b, a)

    def _copy(self, source):
        self.version = source.version
        self.width, self.height = source.width, source.height

        self._bitmap = []
        for row in source._bitmap:
            new_row = []
            for pixel in row:
                new_row.append(pixel[:])

            self._bitmap.append(new_row)

    def _new(self, width, height):
        if width > MAX_WIDTH:
            raise ValueError("Max width is {}, width of {} was given".format(
                MAX_WIDTH, width))

        if height > MAX_HEIGHT:
            raise ValueError("Max height is {}, height of {} was given".format(
                MAX_HEIGHT, height))

        if width < 0:
            raise ValueError("Width can't be less than zero")

        if height < 0:
            raise ValueError("Height can't be less than zero")

        self.version = VERSION
        self.width = width
        self.height = height

        self._bitmap = [[INIT_COLOR, ] * height for j in range(width)]

    def save(self, target):
        if hasattr(target, 'write'):
            self._save_to_file(target)
            return

        if isinstance(target, str):
            with open(target, 'wb') as f:
                self._save_to_file(f)

            return

        raise TypeError(
            "target should be either file path or file-like "
            "object - '{}' instance found instead".format(type(target)))

    def _save_to_file(self, f):
        f.write('OLBMP'.encode('ascii'))
        f.write(bytes((self.version, )))
        f.write(bytes((self.width // 256, self.width % 256)))
        f.write(bytes((self.height // 256, self.height % 256)))
        for pixel in self:
            f.write(bytes(pixel))

    def __getitem__(self, xy):
        j, i = xy
        return self._bitmap[i][j]

    def __setitem__(self, xy, value):
        j, i = xy
        if not hasattr(value, '__iter__'):
            raise TypeError("Pixel color value should be 4-element iterable")

        if len(value) != 4:
            raise ValueError("Pixel color value should be 4-element iterable")

        for component in value:
            if not isinstance(component, int):
                raise TypeError(
                    "Color components should be integers in range(0, 256)")

            if component not in range(0, 256):
                raise ValueError(
                    "Color components should be integers in range(0, 256)")

        self._bitmap[i][j] = value

    def __str__(self):
        return "OLBitMap Image ({}x{})".format(self.width, self.height)

    def __len__(self):
        return self.width * self.height

    def __iter__(self):
        for i in range(self.height):
            for j in range(self.width):
                yield self._bitmap[i][j]
