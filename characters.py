from time import sleep


SPRITES = {
    "Luigi": {
        "normal": (0, 0, 16, 16),
        "prepared": (0, 16, 16, 16),
        "prepared_conv_0": (0, 32, 16, 16),
        "drop": (16, 48, 16, 16),
        "rest_1": (0, 64, 16, 16),
        "rest_2": (0, 80, 16, 16),
    },
    "Mario": {
        "normal": (16, 0, 16, 16),
        "prepared": (16, 16, 16, 16),
        "prepared_conv_0": (16, 32, 16, 16),
        "drop": (0, 48, 16, 16),
        "rest_1": (16, 64, 16, 16),
        "rest_2": (16, 80, 16, 16),
        "carry": (16, 32, 16, 16)
    }
}

class Character:
    def __init__(self, name: str, x: int, y: int, game):
        self.game = game
        self.name = name
        self.__x = x
        self.__y = y
        self.state = "normal"
        self.anim_tick = 0

    def catch(self):
        self.anim_tick = 1

    def update(self):
        if self.anim_tick > 0:
            self.anim_tick += 1
            if self.anim_tick < 4: # 4 ticks prepared
                self.state = "prepared"
            elif self.anim_tick < 10: # 5 ticks drop
                self.state = "drop"
            else:
                self.anim_tick = 0

    @property
    def x(self):
        return self.__x

    @x.setter
    def x(self, value):
        if not isinstance(value, int):
            raise TypeError("x must be an integer")
        if value < 0 or value > 256:
            raise ValueError("x must be non-negative")
        self.__x = value

    @property
    def y(self):
        return self.__y

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
        self.__y = value
        

    def move(self, direction: str):
        try:
            #mario (conv0 different heigh) 
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
