import pyxel

# Constants
SCREEN_W = 256
SCREEN_H = 192
COLOR_BG = 7
COLOR_TEXT = 7

SPRITES = {
    "Mario": {
        "idle": (0, 0, 16, 16),
        "carry": (0, 16, 16, 16),
        "drop": (0, 32, 16, 16),
        "up": (0, 48, 16, 16),
        "down": (0, 48, 16, 16),
    },
    "Luigi": {
        "idle": (16, 0, 16, 16),
        "carry": (16, 32, 16, 16),
        "drop": (16, 16, 16, 16),
        "up": (16, 48, 16, 16),
        "down": (16, 48, 16, 16),
    }
}

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

class Package:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.w = 8
        self.h = 8
        self.color = 10

class Conveyor:
    def __init__(self, x, y, length, direction):
        self.x = x
        self.y = y
        self.length = length
        self.direction = direction 
        self.packages = []

class Truck:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.capacity = 8
        self.load = 0

class Character:
    def __init__(self, name: str, x: int, y: int):
        self.name = name
        self.x = x
        self.y = y
        self.state = "idle"

class Draw:
    def __init__(self):
        pass

    def draw_game(self, game):
        pyxel.cls(COLOR_BG)
        self.draw_background(game.current_difficulty)
        self.draw_hud(game.score, game.failures)
        self.draw_truck(game.truck, game.current_difficulty)
        self.draw_truck_platform(game.truck, game.current_difficulty)
        self.draw_platforms(game.current_difficulty)
        self.draw_ladders(game.current_difficulty)
        
        for conveyor in game.conveyors:
            self.draw_conveyor(conveyor)
        
        self.draw_character(game.mario)
        self.draw_character(game.luigi)

    def draw_background(self, difficulty):
        # Tile the background sprite (80, 80, 16x16) across the screen
        u, v = 80, 80
        w, h = 16, 16
        for y in range(0, SCREEN_H, h):
            for x in range(0, SCREEN_W, w):
                pyxel.blt(x, y, 0, u, v, w, h, 0)

        # Draw some windows
        if difficulty.name== "easy" or difficulty.name== "crazy" :
            pyxel.blt(SCREEN_W*0.75-16 , 80, 0, 80, 112, 32, 16, 0)
            pyxel.blt(SCREEN_W*0.25-3 , 80, 0, 80, 112, 32, 16, 0)
            pyxel.blt(SCREEN_W*0.5-10 , 80, 0, 80, 112, 32, 16, 0)
        if difficulty.name== "medium" or difficulty.name== "easy" or difficulty.name== "crazy" :
            pyxel.blt(SCREEN_W*0.75-16, 60, 0, 80, 112, 32, 16, 0)
            pyxel.blt(SCREEN_W*0.25-3, 60, 0, 80, 112, 32, 16, 0)
            pyxel.blt(SCREEN_W*0.75-16, 40, 0, 80, 112, 32, 16, 0)
            pyxel.blt(SCREEN_W*0.25-3, 40, 0, 80, 112, 32, 16, 0)
            pyxel.blt(SCREEN_W*0.5-10 , 40, 0, 80, 112, 32, 16, 0)
            pyxel.blt(SCREEN_W*0.5-10 , 60, 0, 80, 112, 32, 16, 0)
        if difficulty.name== "extreme" or difficulty.name== "medium" or difficulty.name== "easy" or difficulty.name== "crazy" :
            pyxel.blt(SCREEN_W*0.75-16, 20, 0, 80, 112, 32, 16, 0)
            pyxel.blt(SCREEN_W*0.25-3, 20, 0, 80, 112, 32, 16, 0)
            pyxel.blt(SCREEN_W*0.5-10 , 20, 0, 80, 112, 32, 16, 0)

    def draw_hud(self, score, failures):
        pyxel.text(5, 5, f"Score: {score}", COLOR_TEXT)
        
        if failures > 0: # Draw MISS sprite (u=65, v=217, w=24, h=12)
            pyxel.blt(SCREEN_W - 90, 5, 0, 64, 225, 32, 12, 0)
        
        # Draw Mario heads for misses 
        for i in range(failures):
            pyxel.blt(SCREEN_W - 58 + (i * 18), 2, 0, 96, 80, 15, 15, 0)
    
    def draw_truck_platform(self, truck,difficulty):
        pyxel.blt(0, truck.y+26, 0, 112, 152, 40, 24, 0)
    
    def draw_truck(self, truck,difficulty):
        pyxel.blt(truck.x, truck.y, 0, 36, 86, 42, 26, 0)

    def draw_platforms(self, difficulty):
        # Platform sprite: u=80, v=24, w=32, h=3
        u, v = 80, 24
        w, h = 32, 4
        
        for i in range(difficulty.belts//2+1):
            # Calculate y position (aligned with bottom of characters)
            y = 178 - i * 32
            
            # Luigi's side (Left)
            if i ==0:
                pyxel.blt(24, y-12, 0, u, v, w, h, 0)
            else:
                pyxel.blt(22+w/2, y-12, 0, u, v, w/2, h, 0)
            # Mario's side (Right)
            if i == 0:
                pyxel.blt(212, y, 0, 80, v, w/2, h, 0)
            elif i == 1:
                pyxel.blt(212, y+4, 0, 80, v, w, h, 0)
            else: 
                pyxel.blt(212, y+4, 0, u, v, w/2, h, 0)

    def draw_ladders(self, difficulty):
        # Ladder sprite: u=116, v=24, w=8, h=16 
        u, v = 116, 24
        w, h = 8, 16
        
        for i in range(difficulty.belts//2):
            # Calculate y position (aligned with bottom of characters)
            y = 154 - i * 32
            # Luigi's side (Left)
            pyxel.blt(40, y-16, 0, u, v, w, h, 0)
            # Mario's side (Right)
            pyxel.blt(214, y, 0, u, v, w, h, 0)

    def draw_conveyor(self, conveyor):
        # Mask the background with a black rectangle
        pyxel.rect(conveyor.x-1, conveyor.y+1, conveyor.length+3, 8, 0)

        # Sprite coordinates (we only used the conveyor with borders, so we adjusted the coordinates)
        u_border, v_border = 104, 8
        u_center, v_center = 80, 8
        w_segment = 16
        h = 8 
        
        # 1. Draw Left Border
        pyxel.blt(conveyor.x, conveyor.y, 0, u_border-1, v_border, w_segment+1, h, 0)
        
        # 2. Draw Center 
        start_x = conveyor.x + 17
        end_x = conveyor.x + conveyor.length - 16
        current_x = start_x
        
        while current_x < end_x:
            pyxel.blt(current_x, conveyor.y, 0, u_center, v_center, 16, h, 0)
            current_x += 16
            
        # 3. Draw Right Border
        pyxel.blt(conveyor.x + conveyor.length - w_segment, conveyor.y, 0, u_border, v_border, w_segment+1, h, 0)

    def draw_package(self, package,):
        pyxel.rect(package.x, package.y, package.w, package.h, package.color)

    def draw_character(self, character):
        u, v, w, h = SPRITES[character.name][character.state]
        pyxel.blt(character.x, character.y, 0, u, v, w, h, 0)

class Game:
    def __init__(self):
        pyxel.init(SCREEN_W, SCREEN_H, title="Mario Bros Game & Watch")
        pyxel.load("assets.pyxres")
        
        self.renderer = Draw()

        self.easy = Difficulty("easy", 5, 1, 1, 1, False, 50, 3, False)
        self.medium = Difficulty("medium", 7, 1, 1, 1.5, False, 30, 5, False)
        self.extreme = Difficulty("extreme", 9, 1, 1.5, 2, False, 30, 5, False)
        self.crazy = Difficulty("crazy", 5, 1, 1, 1, True, 20, -1, True)
        self.current_difficulty = self.easy

        # Initialize entities
        self.score = 0
        self.failures = 3 # Temporary for testing
        
        self.init_level()
        
        self.mario = Character("Mario", 212, 162)
        self.luigi = Character("Luigi", 38, 162-12)
        
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
        # Right conveyor (pkg starts)
        self.conveyors.append(Conveyor(230, 166, 36, 1))

    def update(self):
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

    def draw(self):
        self.renderer.draw_game(self)








def main():
    Game()

if __name__ == "__main__":
    main()
