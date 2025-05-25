import pygame as py
from pygame import Vector2, Rect, Surface
from pygame.time import get_ticks
import random as r
import math as m
from collections import deque #permet l'utilisation de queue, plus optimisé que les liste pour ajouter/ retirer des élément au début (FIFO) 
from utils import Label, Button

WIDTH, HEIGHT = 400, 500
FPS = 120 #plus les fps sont élevés, meilleurs sont les collisions

py.init()

screen = py.display.set_mode((WIDTH, HEIGHT)) #flags=py.RESIZABLE
py.display.set_caption("Minesweeper")
py.display.set_icon(py.image.load("flagged_tile.png"))
clock = py.time.Clock()
#Chargement des sprites
sprite_dict = {}
sprite_dict["unrevealed_tile_sprite"] = py.image.load("unrevealed_tile.png").convert_alpha()
sprite_dict["tile_0_sprite"] = py.image.load("revealed_tile.png").convert_alpha()
sprite_dict["tile_1_sprite"] =  py.image.load("tile_1.png").convert_alpha()
sprite_dict["tile_2_sprite"] = py.image.load("tile_2.png").convert_alpha()
sprite_dict["tile_3_sprite"] = py.image.load("tile_3.png").convert_alpha()
sprite_dict["tile_4_sprite"] = py.image.load("tile_4.png").convert_alpha()
sprite_dict["tile_5_sprite"] = py.image.load("tile_5.png").convert_alpha()
sprite_dict["tile_6_sprite"] = py.image.load("tile_6.png").convert_alpha()
sprite_dict["tile_7_sprite"] = py.image.load("tile_7.png").convert_alpha()
sprite_dict["tile_8_sprite"] = py.image.load("tile_8.png").convert_alpha()
sprite_dict["bomb_tile_sprite"] = py.image.load("bomb_tile.png").convert_alpha()
sprite_dict["flagged_tile_sprite"] = py.image.load("flagged_tile.png").convert_alpha()

background_sprite = py.image.load("background.png")
flag_icon = py.transform.scale_by(py.image.load("flag_icon.png").convert_alpha(), 2)
clock_icon = py.transform.scale_by(py.image.load("clock.png").convert_alpha(), 2)





class Timer:
    def __init__(self, duration:int=None, action_to_repeat=None):
        self.active = False
        self.elapsed_time = 0
        self.start_time = 0
        self.current_time = 0
        self.duration = duration
        self.action_to_repeat = action_to_repeat
    
    def update(self):
        if self.active:
            self.current_time = get_ticks()
            self.elapsed_time = self.current_time - self.start_time
            #if self.duration != None and self.action_to_repeat != None:
            if self.elapsed_time %self.duration:
                self.action_to_repeat()

    def start(self):
        self.start_time = get_ticks()
        self.active = True

    def stop(self):
        self.active = False

    def reset(self):
        self.start_time = get_ticks()
        self.elapsed_time = 0

    def get_time_in_second(self)->int:
        return self.elapsed_time // 1000

class Tile:
    def __init__(self, pos:Vector2, value:str, grid_pos:tuple):
        self.pos = pos
        self.grid_pos = grid_pos
        self.size = 32
        self.scale_value = self.size // 16
        self.value = value
        self.unrevealed_sprite = py.transform.scale_by(sprite_dict["unrevealed_tile_sprite"], self.scale_value)
        
        self.flagged_sprite = py.transform.scale_by(sprite_dict["flagged_tile_sprite"], self.scale_value)
        self.is_flagged = False
        self.is_revealed = False
        self.is_hovered = False
        self.rect = Rect(pos.x, pos.y, self.size, self.size)
    
    def update_value(self, value):
        self.value = value
        if value == "x":
            self.revealed_sprite = py.transform.scale_by(sprite_dict[f"bomb_tile_sprite"], self.scale_value)
        else:
            self.revealed_sprite = py.transform.scale_by(sprite_dict[f"tile_{value}_sprite"], self.scale_value)

    def draw(self, screen:Surface):
        if not self.is_revealed and self.is_flagged:
            screen.blit(self.flagged_sprite, self.pos)
        elif self.is_revealed:
            screen.blit(self.revealed_sprite, self.pos)
        else:
            screen.blit(self.unrevealed_sprite, self.pos)

    def handle_events(self, events:py.event.Event):
        global flag_counter
        for event in events:
            if event.type == py.MOUSEMOTION:
                self.is_hovered = Rect.collidepoint(self.rect, event.pos)
            
            elif event.type == py.MOUSEBUTTONDOWN and self.is_hovered and in_game:
                if py.mouse.get_pressed()[0]:
                    if self.value == "-":
                        assign_value_to_grid(tile_grid, self.grid_pos)
                        timer.reset()
                        timer.start()
                        update_timer_label()
                        unflag_all_tiles()
                        update_flag_counter()
                    if self.value == "x":
                        game_over()
                    if self.is_flagged:
                        flag_counter -= 1
                        update_flag_counter()
                    flood_reveal(self.grid_pos)
                    check_win()
                elif py.mouse.get_pressed()[2]:
                    if not self.is_revealed:
                        if self.is_flagged:
                            self.is_flagged = False
                            flag_counter -= 1
                            
                        else:
                            self.is_flagged = True
                            flag_counter += 1
                        update_flag_counter()
                        check_win()


def create_grid(difficulty:int):
    if difficulty <= 1:
        rows = 8
        cols = 6
        bomb = 7
    elif difficulty == 2:
        rows = 8
        cols = 10
        bomb = 10
    elif difficulty == 3:
        rows = 12
        cols = 12
        bomb = 24
    elif difficulty >= 4:
        rows = 24
        cols = 18
        bomb = 80
    grid = []
    bomb_list:list[tuple] = generate_bombs_pos(rows, cols, bomb)
    for _ in range(rows):
        grid.append(["-"]*cols)
    grid = calculate_grid_tiles_value(grid, bomb_list)
    return grid

def assign_value_to_grid(tile_grid, grid_pos):
    global grid

    counter = 0
    while grid[grid_pos[1]][grid_pos[0]] != "0" or counter < 100:
        counter += 1
        grid = create_grid(difficulty)
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            tile_grid[i][j].update_value(grid[i][j])



def generate_bombs_pos(rows:int, cols:int, number:int)->list[tuple]:
    bomb_list:list[tuple] = []
    remaining_bomb = number
    while remaining_bomb > 0:
        pos = tuple((r.randint(0, cols-1), r.randint(0, rows-1)))
        if pos not in bomb_list:
            bomb_list.append(pos)
            remaining_bomb -= 1
    return bomb_list

def get_distance_to_nearest_bomb(bomb_list:list[tuple], pos:tuple):
    d = float('inf')
    for bomb in bomb_list:
        dx = pos[0] - bomb[0]
        dy = pos[1] - bomb[1]
        new_d = m.sqrt(dx**2 + dy**2)
        if new_d < d:
            d = new_d
    return d
    
def calculate_number_of_near_bomb(bomb_list, pos):
    bomb_counter = 0
    for x in range(-1, 2):
        for y in range(-1, 2):
            if x == y == 0:
                continue
            if (pos[0] + x, pos[1] + y) in bomb_list:
                bomb_counter += 1
    return bomb_counter

def calculate_grid_tiles_value(grid, bomb_list:list[tuple]):
    new_grid = grid.copy()
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if (j, i) in bomb_list:
                new_grid[i][j] = "x"
            else:
                distance_to_nearest_bomb = get_distance_to_nearest_bomb(bomb_list, (j, i))
                if distance_to_nearest_bomb >= 2:
                    new_grid[i][j] = "0"
                else:
                    n = str(calculate_number_of_near_bomb(bomb_list, (j, i)))
                    new_grid[i][j] = n
    return new_grid

def flood_reveal(pos):
    height = len(grid)
    width = len(grid[0])
    global tile_revealed
    if tile_grid[pos[1]][pos[0]].is_revealed:
        return
    queue = deque()
    queue.append((pos[0], pos[1]))
    
    while queue:
        cx, cy = queue.popleft()
        if tile_grid[cy][cx].is_revealed:
            continue
        tile_grid[cy][cx].is_revealed = True
        tile_revealed += 1

        if grid[cy][cx] == "0":
            for dy in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    new_x, new_y = cx + dx, cy + dy
                    if 0 <= new_x < width and 0 <= new_y < height:
                        if not tile_grid[new_y][new_x].is_revealed and grid[new_y][new_x] != "x":
                            queue.append((new_x, new_y))

def generate_tile_grid(grid):
    tile_grid = []
    tile_size = 32
    for i in range(len(grid)):
        tile_grid.append([])
        for j in range(len(grid[0])):
            x = WIDTH//2 - len(grid[i]) * tile_size // 2 + j * tile_size
            y = HEIGHT//2 + 50 - len(grid) * tile_size // 2 + i * tile_size
            tile_grid[i].append(Tile(py.Vector2(x, y), "-", (j, i)))
    return tile_grid

def generate_new_grid(difficulty:int):
    global grid
    global tile_grid
    global tile_revealed
    global flag_counter
    tile_revealed = 0
    flag_counter = 0
    grid = create_grid(difficulty)
    tile_grid = generate_tile_grid(grid)

def print_grid(grid):
    for rows in grid:
        print(rows)


def game_over():
    timer.stop()
    reveal_all_tiles()
    global in_game
    global tile_revealed
    tile_revealed = 0
    in_game = False
    restart_button.is_active = True
    print("GAME OVER")

def reveal_all_tiles():
    for row in tile_grid:
        for tile in row:
            tile.is_revealed = True

def unflag_all_tiles():
    global flag_counter
    for sub_list in tile_grid:
        for tile in sub_list:
            tile.is_flagged = False
    flag_counter = 0

def check_win():
    global in_game
    global tile_revealed
    if (difficulty == 1 and tile_revealed == 41) or (difficulty == 2 and tile_revealed == 70)or (difficulty == 3 and tile_revealed == 122):
        timer.stop()
        reveal_all_tiles()
        in_game = False
        restart_button.is_active = True
        tile_revealed = 0
        print("WIN")

def update_flag_counter():
    flag_counter_label.text = str(flag_counter)

def update_timer_label():
    timer_label.text = str(timer.get_time_in_second())

def restart(*args):
    global in_game
    timer.stop()
    generate_new_grid(difficulty)
    in_game = True
    restart_button.is_active = False

grid = []
tile_grid:list[list[Tile]] = []
title = Label("Minesweeper", py.Rect(WIDTH//2, 30, 150, 50), 50)
flag_counter_label = Label("0", py.Rect(WIDTH//2 - 35, 80, 20, 20), 35)
flag_counter_icon = Label("", py.Rect(WIDTH//2 - 70, 80, 20, 20), sprite=flag_icon)
timer_label = Label("0", py.Rect(WIDTH//2 + 60, 80, 20, 20), 35)
timer_icon = Label("", py.Rect(WIDTH//2 + 25, 80, 20, 20), sprite=clock_icon)
timer = Timer(1000, update_timer_label)
restart_button = Button("Restart", py.Rect(WIDTH//2, HEIGHT- 30, 100, 50), 30, (255, 255 ,255), (255, 255, 255), action=restart, border=True)
labels_list = [title, flag_counter_label, flag_counter_icon, timer_label, timer_icon]
restart_button.is_active = False
tile_revealed = 0
flag_counter = 0


difficulty = 2

generate_new_grid(difficulty)
running = True
in_game = True
while running:
    dt = clock.tick(FPS) / 1000

    events = py.event.get()
    for event in events:
        if event.type == py.QUIT:
            running = False
        elif event.type == py.KEYDOWN:
            keys = py.key.get_pressed()
            if keys[py.K_r]:
                restart()
    
    timer.update()
    restart_button.handle_events(events)
    
    for row in tile_grid:
        for tile in row:
            tile.handle_events(events)

    screen.fill((50, 50, 50))
    screen.blit(background_sprite, (0, 0))
    for label in labels_list:
        label.draw(screen)

        
    restart_button.draw(screen)

    for row in tile_grid:
        for tile in row:
            tile.draw(screen)
    
    py.display.flip()

py.quit()
