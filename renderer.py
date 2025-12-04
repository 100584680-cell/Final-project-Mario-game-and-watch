import pyxel
from entities import Conveyor, Truck, Package
# Constants
SCREEN_W = 256
SCREEN_H = 192
COLOR_BG = 7
COLOR_TEXT = 7

class Renderer:
    def __init__(self):
        pass

    def draw_game(self, game):
        pyxel.cls(COLOR_BG)
        self.draw_background(game)
        self.draw_hud(game.score, game.failures)
        self.draw_truck(game.truck, game.current_difficulty)
        self.draw_truck_platform(game.truck, game.current_difficulty)
        self.draw_platforms(game.current_difficulty)
        self.draw_ladders(game.current_difficulty)
        for conveyor in game.conveyors:
            self.draw_conveyor(conveyor)
        
        self.draw_middle_column(game)
        
        for pkg in game.packages:
            self.draw_package(pkg)

        self.draw_character(game.mario)
        self.draw_character(game.luigi)

        if game.game_over:
            self.draw_game_over()

#TEMPORAL
    def draw_game_over(self):
        pyxel.text(SCREEN_W // 2 - 20, SCREEN_H // 2, "GAME OVER", 8)

    def draw_middle_column(self, game):
        for i in range(game.end_y-22 , SCREEN_H, 8):
            pyxel.blt(SCREEN_W*0.5-10,i, 0, 112, 192, 32, 8, 0)

    def draw_background(self, game):
        difficulty = game.current_difficulty
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
    
    def draw_truck_platform(self, truck, difficulty):
        pyxel.blt(0, truck.y+26, 0, 112, 152, 40, 24, 0)
    
    def draw_truck(self, truck, difficulty):
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
        pyxel.rect(conveyor.x, conveyor.y+3, conveyor.length, 4, 0)

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

    def draw_package(self, package):
        # Define sprites for each height: (u, v)
        package_sprites = {
            152: (32, 0),  # Bottom level
            136: (32, 16),  # Level 2
            120: (32, 32),  # Level 3
            104:  (32, 48),  # Level 4
            88:  (32, 64),  # Top level
        }
        if package.show_miss_rect:
            pyxel.rect(198, 152, 10, 16, 0)
        
        if package.y in package_sprites:
            u, v = package_sprites[package.y]
            if package.x < 55:
                u = 64
            if package.x > 195 and package.y<152:
                u = 48
            pyxel.blt(package.x, package.y, 0, u, v, 13, 16, 0)
       

    def draw_character(self, character):
        from characters import SPRITES # Import SPRITES here to avoid circular dependency if needed, or move SPRITES to a shared file
        u, v, w, h = SPRITES[character.name][character.state]
        pyxel.blt(character.x, character.y, 0, u, v, w, h, 0)
