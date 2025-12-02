class Package:
    def __init__(self, x, y):
        self._x = 0
        self._y = 0
        self.x = x
        self.y = y
        self.w = 8
        self.h = 8
        self.color = 10

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        if not isinstance(value, int):
            raise TypeError("x must be an integer")
        if value < 0:
            raise ValueError("x must be non-negative")
        self._x = value

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        if not isinstance(value, int):
            raise TypeError("y must be an integer")
        if value < 0:
            raise ValueError("y must be non-negative")
        self._y = value

class Conveyor:
    def __init__(self, x, y, length, direction):
        self._x = 0
        self._y = 0
        self.x = x
        self.y = y
        self.length = length
        self.direction = direction 
        self.packages = []

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        if not isinstance(value, int):
            raise TypeError("x must be an integer")
        if value < 0:
            raise ValueError("x must be non-negative")
        self._x = value

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        if not isinstance(value, int):
            raise TypeError("y must be an integer")
        if value < 0:
            raise ValueError("y must be non-negative")
        self._y = value

class Truck:
    def __init__(self, x, y):
        self._x = 0
        self._y = 0
        self.x = x
        self.y = y
        self.capacity = 8
        self.load = 0

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        if not isinstance(value, int):
            raise TypeError("x must be an integer")
        if value < 0:
            raise ValueError("x must be non-negative")
        self._x = value

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        if not isinstance(value, int):
            raise TypeError("y must be an integer")
        if value < 0:
            raise ValueError("y must be non-negative")
        self._y = value
