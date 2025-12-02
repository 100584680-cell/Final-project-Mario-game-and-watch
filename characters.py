from time import sleep

SPRITES = {
    "Luigi": {
        "idle": (0, 0, 16, 16),
        "carry": (0, 16, 16, 16),
        "drop": (0, 32, 16, 16),
        "up": (0, 48, 16, 16),
        "down": (0, 48, 16, 16),
    },
    "Mario": {
        "idle": (16, 0, 16, 16),
        "carry": (16, 32, 16, 16),
        "drop": (16, 16, 16, 16),
        "up": (16, 48, 16, 16),
        "down": (16, 48, 16, 16),
    }
}

class Character:
    def __init__(self, name: str, x: int, y: int, game):
        self.game = game
        self.name = name
        self._x = x
        self._y = y
        self.state = "idle"

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        if not isinstance(value, int):
            raise TypeError("x must be an integer")
        if value < 0 or value > 256:
            raise ValueError("x must be non-negative")
        self._x = value

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        if not isinstance(value, int):
            raise TypeError("y must be an integer")
        if value < 0 or value > 162:
            raise ValueError("y must be non-negative")
        if self.game.current_difficulty.name == "easy" or self.game.current_difficulty.name == "crazy":
            if value < 80:
                raise ValueError("Character can't fly")
        elif self.game.current_difficulty.name == "medium":
            if value < 50:
                raise ValueError("Character can't fly")
        elif self.game.current_difficulty.name == "extreme":
            if value < 20:
                raise ValueError("Character can't fly")
        self._y = value
        

    def move(self, direction: str):
        try:
            if direction == "up":
                if self.y == 162:
                    self.y -= 28 
                else:
                    self.y -= 32    
            elif direction == "down":
                if self.y == 134:
                    self.y += 28   
                else:
                    self.y += 32
        except ValueError:
            pass
