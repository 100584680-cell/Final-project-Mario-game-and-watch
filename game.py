import pyxel
from renderer import Renderer
from characters import Character
from entities import Truck, Conveyor, Package
import random
import time

# Constants
SCREEN_W = 256 
SCREEN_H = 192

class Difficulty:
    """
    Configuration for game difficulty levels.
    Controls belt count, speeds, spawn rates, and scoring rules.    (could be several dictionaries)
    """
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
    """
    Main game controller.
    Manages the game loop, state, input, and entities.
    """
    def __init__(self):
        pyxel.init(SCREEN_W, SCREEN_H, title="Mario Bros Game & Watch")
        pyxel.load("assets.pyxres")

        self.in_menu = True  # Show main menu before starting
        
        self.renderer = Renderer()

        self.easy = Difficulty("easy", 5, 1, 1, 1, False, 50, 3, False)
        self.medium = Difficulty("medium", 7, 1, 1, 1.5, False, 30, 5, False)
        self.extreme = Difficulty("extreme", 9, 1, 1.5, 2, False, 30, 5, False)
        self.crazy = Difficulty("crazy", 5, 1, 1, 1, True, 20, -1, True)
        self.current_difficulty = self.easy

        # Initialize entities
        self.score = 0
        self.failures = 0
        self.game_over = False
        self.spawn_timer = 40
        self.boss_timer = 0
        self.boss_active = False
        
        self.init_level()
        
        self.mario = Character("Mario", 212, 162, self)
        self.luigi = Character("Luigi", 38, 162-12, self)
        self.packages = [Package(230, 152, self)]
        
        pyxel.run(self.update, self.draw)

    def init_level(self):
        """
        Sets up the level based on the current difficulty configuration.
        Initializes truck position and number of conveyor belts.
        """
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
        """
        Main game loop update function.
        Handles:
        1. Menu input
        2. Game Over input
        3. Character movement input
        4. Package spawning logic
        5. Entity updates (packages, characters, collisions)
        """
        # Handle main menu input
        if self.in_menu:
            if pyxel.btnp(pyxel.KEY_1):
                self.current_difficulty = self.easy
                self.reset_game()
                self.in_menu = False
            elif pyxel.btnp(pyxel.KEY_2):
                self.current_difficulty = self.medium
                self.reset_game()
                self.in_menu = False
            elif pyxel.btnp(pyxel.KEY_3):
                self.current_difficulty = self.extreme
                self.reset_game()
                self.in_menu = False
            elif pyxel.btnp(pyxel.KEY_4):
                self.current_difficulty = self.crazy
                self.reset_game()
                self.in_menu = False
            elif pyxel.btnp(pyxel.KEY_Q):
                pyxel.quit()
            return  # Skip game logic while in menu
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
        
        # Handle Game Over state
        if self.game_over:
            if pyxel.btnp(pyxel.KEY_R):  # Restart game
                self.reset_game()
            elif pyxel.btnp(pyxel.KEY_M):  # Back to menu
                self.in_menu = True
                self.game_over = False
            elif pyxel.btnp(pyxel.KEY_Q):  # Quit
                pyxel.quit()
            return
        


        if self.game_over:
            return

        if pyxel.btnp(pyxel.KEY_UP):
            self.mario.move("up")
        if pyxel.btnp(pyxel.KEY_DOWN):
            self.mario.move("down")
        if pyxel.btnp(pyxel.KEY_W):
            self.luigi.move("up")
        if pyxel.btnp(pyxel.KEY_S):
            self.luigi.move("down")

        # Spawn logic
        if self.spawn_timer > 0:
            self.spawn_timer -= 1

        max_packages = 1 + (self.score // self.current_difficulty.min_pkg_increment)
        
        # Check if we can spawn a new package (spawn area clear)
        spawn_clear = True
        for pkg in self.packages:
            if pkg.x > 210 and pkg.y == 152: # Check if any package is in the spawn zone
                spawn_clear = False
        
        if len(self.packages) < max_packages and spawn_clear and self.spawn_timer == 0:
            self.packages.append(Package(230, 152, self))
            self.spawn_timer = random.randint(35, 40) # Wait 15-20 frames before next spawn check

        # Reset character states
        self.mario.state = "normal"
        self.luigi.state = "normal"

        # Update all packages
        for pkg in self.packages:
            pkg.pkg_movement()
            
            # Check for delivered
            if pkg.state == "delivered":
                self.packages.remove(pkg)
                self.score += 1
                continue

            # Check for miss 
            if pkg.x < 15:
                self.failures += 1
                self.packages.remove(pkg)
                self.boss_side = "left"
                self.boss_timer = 60 # Set timer for boss animation

            if pkg.x > 240:
                self.failures += 1
                self.packages.remove(pkg)
                self.boss_side = "right"
                self.boss_timer = 60 # Set timer for boss animation
                
            # Update character states based on package proximity
            pkg.show_miss_rect = False
            pkg.caught = False
            pkg.check_proximity(self.mario)
            pkg.check_proximity(self.luigi)

        self.mario.update()
        self.luigi.update()

        if self.failures >= 3:
            self.game_over = True

        


    def draw(self):
        # Show main menu screen
        if self.in_menu:
            self.renderer.draw_menu()
            return  # Skip game rendering while in menu
        
        # Show Game Over screen
        if self.game_over:
            self.renderer.draw_game_over()
            return

        # Normal game rendering
        self.renderer.draw_game(self)

    def reset_game(self):
        self.score = 0
        self.failures = 0
        self.packages = [Package(230, 152, self)]
        self.spawn_timer = 100
        self.game_over = False
        self.boss_active = False
        self.init_level()
        self.mario = Character("Mario", 212, 162, self)
        self.luigi = Character("Luigi", 38, 150, self)
