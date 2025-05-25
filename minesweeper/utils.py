import pygame as py
from pygame import Vector2


class Label:
    def __init__(self, text:str="", 
                 rect:py.Rect=py.Rect(0, 0, 10, 10), 
                 font_size:int=24, 
                 color:py.Color=(255, 255, 255), 
                 sprite=None, 
                 border:bool=False, border_width:int=3, border_radius:int=3, 
                 border_hover_color=None, hover_rect:py.Rect=None):
        self.text = text
        self.rect = rect
        self.font_size = font_size
        self.color = color

        self.sprite = sprite
        self.font = py.font.Font(None, font_size)
        self.border = border
        self.border_width = border_width
        self.border_radius = border_radius
        self.border_hover_color = border_hover_color
        self.is_hovered = False
        self.hover_rect = hover_rect
        
        

        self.border_rect = rect.copy()
        self.sprite_rect = rect.copy()

        self.border_rect.center = (self.rect[0], self.rect[1]) #Centre la bordure autour de pos_x/ pos_y
        self.hover_rect = self.hover_rect if self.hover_rect != None else self.border_rect
        
        if self.sprite:
            self.sprite_rect[0] -= self.sprite.get_rect()[2]//2 #centre le rectangle du sprite autour de pos_x/ pos_y
            self.sprite_rect[1] -= self.sprite.get_rect()[3]//2  
        
    def draw(self, screen:py.Surface):
        
        color = self.color
        if self.border:
            self.border_rect.center = (self.rect[0], self.rect[1]) #Centre la bordure autour de pos_x/ pos_y
            self.hover_rect = self.hover_rect if self.hover_rect != None else self.border_rect
            if self.border_hover_color != None and self.is_hovered:
                border_color = self.border_hover_color
            else:
                border_color = color
            py.draw.rect(screen, border_color, self.border_rect, self.border_width, 3)
        if self.sprite: screen.blit(self.sprite, self.sprite_rect)
        text = self.font.render(self.text, True, color)
        text_rect = text.get_rect(center= (self.rect[0], self.rect[1]))
        screen.blit(text, text_rect)
    
    def handle_events(self, events:py.event.Event):
        for event in events:
            if event.type == py.MOUSEMOTION:
                self.is_hovered =  py.Rect.collidepoint(self.hover_rect, event.pos)


class Button:
    def __init__(self, 
                 text:str="", 
                 rect:py.Rect=py.Rect(0, 0, 10, 10), 
                 font_size:int=24, 
                 color:py.Color=(255, 255, 255), hover_color:py.Color=(200, 200, 200), 
                 action=None, action_arg=None, 
                 sprite=None, 
                 border:bool=False, border_width:int=3, border_radius:int=3, 
                 sound=None):
        self.text = text
        self.rect:py.Rect = rect
        self.font_size = font_size
        self.color = color
        self.hover_color = hover_color
        self.action = action
        self.action_arg = action_arg
        self.sprite:py.Surface = sprite
        self.font = py.font.Font(None, font_size)
        self.border = border
        self.border_width = border_width
        self.border_radius = border_radius
        self.is_active = True
        #if sound:
            #self.sound = assets_manager.get_sound(sound)
        #else:
            #self.sound = False
        
        self.is_hovered = False

        self.border_rect = rect.copy()
        self.sprite_rect = rect.copy()
        self.border_rect.center = (rect[0], rect[1]) #Centre la bordure autour de pos_x/ pos_y
         
        
    def draw(self, screen:py.Surface):
        if not self.is_active:
            return
        color = self.hover_color if self.is_hovered else self.color
        if self.border:
            py.draw.rect(screen, color, self.border_rect, self.border_width, 3)
        if self.sprite:
            pos = Vector2(self.rect[0], self.rect[1])
            sprite_width = self.sprite.get_width()
            sprite_height = self.sprite.get_height()
            draw_rect = (pos.x - sprite_width//2, pos.y - sprite_height//2)
            screen.blit(self.sprite, draw_rect)
        if self.text != '':
            text = self.font.render(self.text, True, color)
            text_rect = text.get_rect(center= (self.rect[0], self.rect[1]))
            screen.blit(text, text_rect)
        
        
    def handle_events(self, events:py.event.Event):
        for event in events:
            if event.type == py.MOUSEMOTION:
                self.is_hovered =  py.Rect.collidepoint(self.border_rect, event.pos)

            elif event.type == py.MOUSEBUTTONDOWN and self.is_hovered and py.mouse.get_pressed()[0] and self.is_active:
                #if self.sound:
                    #py.mixer.Sound(self.sound).play()
                self.action(self.action_arg)
