class Package:
    """
    Represents a package moving through the conveyor belts.
    Handles its own movement logic, state (normal, falling, delivered),
    and interacts with the truck and characters.
    """
    def __init__(self, x, y, game):
        self.x = x
        self.y = y
        self.game = game
        self.state = "normal"
        self.caught = False # track if caught by a character
        self.carrier = None
        self.floor = 0
        self.aux_pkg = 0 # auxiliary counter for movement timing
        self.direction = ""

    @property
    def state(self):
        return self.__state

    @state.setter
    def state(self, value):
        if not isinstance(value, str):
            raise TypeError("State must be a string")
        self.__state = value

    @property
    def luigi_y(self):
        return self.game.luigi.y

    @property
    def current_difficulty(self):
        return self.game.current_difficulty

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
        """
        Calculates the package's next position based on its location,
        the current difficulty (which dictates belt layout), and its state.
        """
        # Reset state to normal if it was falling (ensures 1-tick duration)
        if self.state == "falling":
            self.state = "normal"
        self.aux_pkg += 1                   
        
        if self.current_difficulty.name == "easy" or self.current_difficulty.name == "crazy":
            package_last_y = 152-32*2
            luigi_last_y = 150-32*2
        elif self.current_difficulty.name == "medium":
            package_last_y = 152-32*3
            luigi_last_y = 150-32*3
        elif self.current_difficulty.name == "extreme":
            package_last_y = 152-32*4
            luigi_last_y = 150-32*4
        
        #check for truck 
        if self.x < 45 and self.y == package_last_y and self.game.luigi.y == luigi_last_y:
            self.game.truck.load_package()
            self.state = "delivered"

        # height change
        #Luigi
        elif self.x < 45:
            if self.caught:
                self.y -= 16
                self.x += 10
                self.state = "falling"
            elif self.y < 152:
                 self.y += 5 # Fall off
        
        #Mario
        if self.x > 195:
            if self.caught:
                self.y -= 16
                # Snap to grid
                self.y = round((self.y - 8) / 16) * 16 + 8
                self.x -= 10
                self.state = "falling"
            elif self.y < 152:
                self.y += 5 # Fall off

        if self.aux_pkg%9==0:
            #skip middle column
            if self.x<152 and self.x>118 and self.direction == "left":
                self.x=104
            elif self.x>100 and self.x<150 and self.direction == "right":
                self.x=150
            #normal movement
            elif self.y == 152 or self.y == 152-32 or self.y == 152-32*2 or self.y == 152-32*3 or self.y ==152-32*4:
                self.x -= 10
                self.direction = "left"
            else:
                self.x += 10 
                self.direction = "right"
    
    def check_proximity(self, character):
        # Mario (Right side)
        if character.name == "Mario":
            if self.x > 175 and abs(self.y - character.y) <3  and self.y > character.y:
                if not self.caught:
                    self.caught = True
                    character.catch()
                character.state = "prepared"


        # Luigi (Left side)
        elif character.name == "Luigi":
            if self.x < 65 and abs(self.y - character.y) < 3 and self.y > character.y:
                if not self.caught:
                    self.caught = True
                    character.catch()
                character.state = "prepared"


class Conveyor:
    """
    Represents a static conveyor belt segment.
    Mainly used for rendering and verifying platform positions.
    """
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
    """
    Represents the delivery truck.
    Collects packages and has a delivery animation sequence.
    """
    def __init__(self, x, y):
        self.__x = 0
        self.__y = 0
        self.x = x
        self.y = y
        self.capacity = 8
        self.load = 0
        self.state = "waiting"    # waiting, delivering, returning

    @property
    def state(self):
        return self.__state

    @state.setter
    def state(self, value):
        if not isinstance(value, str):
            raise TypeError("State must be a string")
        self.__state = value

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



    def load_package(self):
        if self.state == "waiting":
            self.load += 1
            if self.load >= self.capacity:
                self.state = "delivering"

    def update(self):
        # Truck delivering animation
        if self.state == "delivering":
            self.x -= 2  # move left
            if self.x < -50:  # off screen
                self.state = "returning"
                self.load = 0

        # Truck returning empty
        if self.state == "returning":
            self.x += 2  # move right
            if self.x >= 200:  # original position
                self.state = "waiting"