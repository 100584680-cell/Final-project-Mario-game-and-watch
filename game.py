import pyxel
from renderer import Renderer
from characters import Character
from entities import Truck, Conveyor, Package
import time

# Constants
SCREEN_W = 256  
SCREEN_H = 192

class Difficulty:
    def __init__(
            self,
            name: str,
            belts: int,
            velocity_c0: float,
            velocity_even: float,
            velocity_odd: float,
            random_per_belt: bool,
            min_pkg_increment: int,
            truck_remove_every: int,
            invert_controls: bool,
        ):
            self.name = name
            self.belts = belts
            self.velocity_c0 = velocity_c0
            self.velocity_even = velocity_even
            self.velocity_odd = velocity_odd
            self.random_per_belt = random_per_belt
            self.min_pkg_increment = min_pkg_increment
            self.truck_remove_misses = truck_remove_every
            self.invert_controls = invert_controls

class Game:
    def __init__(self):
        pyxel.init(SCREEN_W, SCREEN_H, title="Mario Bros Game & Watch")
        pyxel.load("assets.pyxres")
        
        self.renderer = Renderer()

        self.easy = Difficulty("easy", 5, 1, 1, 1, False, 50, 3, False)
        self.medium = Difficulty("medium", 7, 1, 1, 1.5, False, 30, 5, False)
        self.extreme = Difficulty("extreme", 9, 1, 1.5, 2, False, 30, 5, False)
        self.crazy = Difficulty("crazy", 5, 1, 1, 1, True, 20, -1, True)
        self.current_difficulty = self.easy

        # Initialize entities
        self.score = 0
        self.failures = 3 # Temporary for testing
        
        self.init_level()
        
        self.mario = Character("Mario", 212, 162, self)
        self.luigi = Character("Luigi", 38, 162-12, self)
        
        pyxel.run(self.update, self.draw)

    def init_level(self):
        # Determine truck position
        if self.current_difficulty.name == "easy" or self.current_difficulty.name == "crazy":
            self.truck = Truck(0, 94)
        elif self.current_difficulty.name == "medium":
            self.truck = Truck(0, 62)
        else:
            self.truck = Truck(0, 30)

        # Create conveyors
        self.conveyors = []
        for i in range(self.current_difficulty.belts):
            y = 166 - i * 16            # each 16 pixel the conveyor repeats
            self.conveyors.append(Conveyor(62, y, 144, 1))
            self.end_y = y
        # Right conveyor (pkg starts)
        self.conveyors.append(Conveyor(230, 166, 36, 1))

    def update(self):
        time.sleep(0.05)
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
        
        difficulty_changed = False
        if pyxel.btnp(pyxel.KEY_1):
            self.current_difficulty = self.easy
            self.init_level()
        if pyxel.btnp(pyxel.KEY_2):
            self.current_difficulty = self.medium
            self.init_level()
        if pyxel.btnp(pyxel.KEY_3):
            self.current_difficulty = self.extreme
            self.init_level()
        if pyxel.btnp(pyxel.KEY_4):
            self.current_difficulty = self.crazy
            self.init_level()


        if pyxel.btnp(pyxel.KEY_UP):
            self.mario.move("up")
        if pyxel.btnp(pyxel.KEY_DOWN):
            self.mario.move("down")
        if pyxel.btnp(pyxel.KEY_W):
            self.luigi.move("up")
        if pyxel.btnp(pyxel.KEY_S):
            self.luigi.move("down")


    def draw(self):
        self.renderer.draw_game(self)
