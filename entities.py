class Package:
    def __init__(self, x, y):
        self.__x = 0        
        self.__y = 0
        self.aux_pkg = 0
        self.x = x
        self.y = y
        self.state = "normal"
        self.caught = False

    @property
    def x(self):
        return self.__x

    @x.setter
    def x(self, value):
        if not isinstance(value, int):
            raise TypeError("x must be an integer")
        if value < 0:
            raise ValueError("x must be non-negative")
        self.__x = value

    @property
    def y(self):
        return self.__y

    @y.setter
    def y(self, value):
        if not isinstance(value, int):
            raise TypeError("y must be an integer")
        if value < 0:
            raise ValueError("y must be non-negative")
        self.__y = value


    def pkg_movement(self):
        # Reset state to normal if it was falling (ensures 1-tick duration)
        if self.state == "falling":
            self.state = "normal"

        self.aux_pkg += 1 
        # height change
        if self.x <45:
            if self.caught:
                self.y -= 16
                self.x += 10
                self.state = "falling"
            else:
                 self.x -= 10 # Fall off
        if self.x > 195 and self.y<152:
            if self.caught:
                self.y -= 16
                self.x -= 10
                self.state = "falling"
            else:
                self.x += 10 # Fall off

        if self.aux_pkg%9==0:
            if self.y == 152 or self.y == 152-32 or self.y == 152-32*2 or self.y == 152-32*3 or self.y ==152-32*4:
                self.x -= 10
            else:
                self.x += 10 
    
    def check_proximity(self, character):
        # Mario (Right side)
        if character.name == "Mario":
            if self.x > 165 and abs(self.y - character.y) < 20 and self.y > character.y:
                character.state = "prepared"
                self.caught = True
            else:
                character.state = "normal"

        # Luigi (Left side)
        elif character.name == "Luigi":
            if self.x < 75 and abs(self.y - character.y) < 20 and self.y > character.y:
                character.state = "prepared"
                self.caught = True
            else:
                character.state = "normal"  
        
        
class Conveyor:
    def __init__(self, x, y, length, direction):
        self.__x = 0
        self.__y = 0
        self.x = x
        self.y = y
        self.length = length
        self.direction = direction 
        self.packages = []

    @property
    def x(self):
        return self.__x

    @x.setter
    def x(self, value):
        if not isinstance(value, int):
            raise TypeError("x must be an integer")
        if value < 0:
            raise ValueError("x must be non-negative")
        self.__x = value

    @property
    def y(self):
        return self.__y

    @y.setter
    def y(self, value):
        if not isinstance(value, int):
            raise TypeError("y must be an integer")
        if value < 0:
            raise ValueError("y must be non-negative")
        self.__y = value

class Truck:
    def __init__(self, x, y):
        self.__x = 0
        self.__y = 0
        self.x = x
        self.y = y
        self.capacity = 8
        self.load = 0

    @property
    def x(self):
        return self.__x

    @x.setter
    def x(self, value):
        if not isinstance(value, int):
            raise TypeError("x must be an integer")
        if value < 0:
            raise ValueError("x must be non-negative")
        self.__x = value

    @property
    def y(self):
        return self.__y

    @y.setter
    def y(self, value):
        if not isinstance(value, int):
            raise TypeError("y must be an integer")
        if value < 0:
            raise ValueError("y must be non-negative")
        self.__y = value
