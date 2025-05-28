import pygame as py
import random as r
import numpy as np
import math as m
from collections import deque

WIDTH, HEIGHT = 400, 500
FPS = 60

use_ai = False

py.init()
screen = py.display.set_mode((WIDTH, HEIGHT))
py.display.set_caption("Minesweeper")
py.display.set_icon(py.image.load("flag_icon.png"))
clock = py.time.Clock()

def load_sprites()->dict[py.Surface]:
    sprites = {}
    sprites["unrevealed_tile_sprite"] = py.image.load("unrevealed_tile.png").convert_alpha()
    sprites["tile_0_sprite"] = py.image.load("revealed_tile.png").convert_alpha()
    sprites["tile_1_sprite"] =  py.image.load("tile_1.png").convert_alpha()
    sprites["tile_2_sprite"] = py.image.load("tile_2.png").convert_alpha()
    sprites["tile_3_sprite"] = py.image.load("tile_3.png").convert_alpha()
    sprites["tile_4_sprite"] = py.image.load("tile_4.png").convert_alpha()
    sprites["tile_5_sprite"] = py.image.load("tile_5.png").convert_alpha()
    sprites["tile_6_sprite"] = py.image.load("tile_6.png").convert_alpha()
    sprites["tile_7_sprite"] = py.image.load("tile_7.png").convert_alpha()
    sprites["tile_8_sprite"] = py.image.load("tile_8.png").convert_alpha()
    sprites["bomb_tile_sprite"] = py.image.load("bomb_tile.png").convert_alpha()
    sprites["flagged_tile"] = py.image.load("flagged_tile.png").convert_alpha()
    return sprites

class GameModel:
    #Contient toute la logique du jeu qui doit pouvoir tourner sans pygame 
    def __init__(self, rows, cols, num_bombs):
        self.rows = rows
        self.cols = cols
        self.num_bombs = num_bombs

        self.grid = self._generate_grid()
        self.revealed = [[False] * cols for _  in range(rows)]
        self.flagged = [[False]* cols for _ in range(rows)]
        
        self.game_over = False
        self.victory = False
        self.tiles_revealed = 0
        self.total_safe_tiles = rows * cols - num_bombs
        
        self.reveal(1, 1)
        self.toggle_flag(7, 7)

    def _generate_grid(self):
        #l'underscore signifie que la fonction est désignée
        #  pour une utilisation interne au scope

        grid = [["0" for _ in range(self.cols)] for _ in range(self.rows)]
        #tire des nombre aléatoire en 1 dim
        #puis retranscri les coordonées de 2dim
        bombs_position = r.sample(range(self.rows * self.cols), self.num_bombs)
        for bomb in bombs_position:
            y, x = divmod(bomb, self.cols)
            grid[y][x] = "x"

        #Calcul les valeurs des différentes cases
        for y in range(self.rows):
            for x in range(self.cols):
                if grid[y][x] == "x":
                    continue
                counter = 0
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        ny, nx = y + dy, x + dx
                        if 0 <= ny < self.rows and 0 <= nx < self.cols:
                            if grid[ny][nx] == "x":
                                counter += 1
                grid[y][x] = str(counter)
        return grid
    
    def in_bounds(self, x, y)->bool:
        return  0 <= y < self.rows and 0 <= x < self.cols

    def reveal(self, x:int, y:int)->None:
        if not self.in_bounds(x, y):
            return
        if self.revealed[y][x] or self.flagged[y][x] or self.game_over:
            return
        if self.grid[y][x] == "x":
            self.revealed[y][x] = True
            self.game_over = True
            return
        self._flood_fill(x, y)
        self._check_victory()

    def _flood_fill(self, x:int, y:int):

        queue = deque()
        queue.append((x, y))

        while queue:
            cx, cy = queue.popleft()
            if not self.in_bounds(cx, cy):
                continue
            if self.revealed[cy][cx]:
                continue

            self.revealed[cy][cx] = True
            self.tiles_revealed += 1
            if self.flagged[cy][cx]:
                self.flagged[cy][cx] = False
            
            if self.grid[cy][cx] == "0":
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        if dx == dy == 0:
                            continue
                        ny, nx = cy + dy, cx + dx
                        if self.in_bounds(nx, ny) and not self.revealed[ny][nx]:
                            queue.append((nx, ny))

                    


    def toggle_flag(self, x:int, y:int)->None:
        if not self.in_bounds(x, y) or self.revealed[y][x] or self.game_over:
            return
        self.flagged[y][x] = not self.flagged[y][x]
    
    def _check_victory(self):
        if self.tiles_revealed == self.total_safe_tiles:
            self.victory = True
            self.game_over = True

    def get_tile(self, x, y):
        if not self.in_bounds(x, y):
            return None
        if self.revealed[y][x]:
            return self.grid[y][x]
        elif self.flagged[y][x]:
            return "f"
        else:
            return "-" #unknown

    
class GameView:
    def __init__(self, model:GameModel):
        self.model = model
        self.width = model.cols
        self.height = model.rows
        self.sprites = self._prepare_scaled_sprites(load_sprites())
        self.tile_size = 32
        self.offset_x = WIDTH // 2 - self.width * self.tile_size // 2
        self.offset_y = HEIGHT // 2 - self.height * self.tile_size // 2
    
    def draw(self, screen:py.Surface)->None:
        screen.fill((50, 50, 70))
        for i in range(self.height):
            for j in range(self.width):
                sprite = self._get_sprite(j, i)
                screen.blit(sprite, (
                    self.offset_x + j * self.tile_size,
                    self.offset_y + i * self.tile_size
                ))

    def _prepare_scaled_sprites(self, raw_sprites:dict[py.Surface]):
        return {
            key: py.transform.scale2x(sprite)
            for key, sprite in raw_sprites.items()
    }

    def _get_sprite(self, x:int, y:int)->py.Surface:
        if not self.model.revealed[y][x]:
            if self.model.flagged[y][x]:
                return self.sprites["flagged_tile"]
            return self.sprites["unrevealed_tile_sprite"]
        value = self.model.grid[y][x]
        if value == 'x':
            return self.sprites["bomb_tile_sprite"]
        return self.sprites[f"tile_{value}_sprite"]


class GameController:
    def __init__(self, model:GameModel):
        self.model = model

    
    def handle_user_input(self, events)->None:
        pass

    def handle_mouse_click(self, x:int, y:int, button:str)->None:
        if button == "left":
            self.model.reveal(x, y)
        elif button == "right":
            self.model.toggle_flag(x, y)


class SolverAgent:
    def __init__(self, model:GameModel):
        self.model = model


    def make_move(self)->None:
        pass



model = GameModel(8, 10, 10)
view = GameView(model)
controller = GameController(model)
agent = SolverAgent(model) if use_ai else None

running = True
while running:
    dt = clock.tick(FPS) / 1000

    events = py.event.get()
    for event in events:
        if event.type == py.QUIT:
            running = False

    if use_ai:
        agent.make_move()
    else:
        controller.handle_user_input(events)
    
    view.draw(screen)
    py.display.flip()

py.quit()