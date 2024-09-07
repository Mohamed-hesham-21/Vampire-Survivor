from typing import List
from pygame import Surface
from pygame.rect import FRect, Rect
from settings import *

class All_Sprites(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.Vector2()
    
    def draw(self , target_position):
        self.offset.x = target_position[0] - WORLD_WIDTH / 2
        self.offset.y = target_position[1] - WORLD_HEIGHT / 2

        Tiles = [sprite for sprite in self if hasattr(sprite, 'ground')]
        objects = [sprite for sprite in self if not hasattr(sprite, 'ground')]
        for layer in [Tiles, objects]:
            for sprite in sorted(layer , key = lambda x : x.rect.centery):
                self.display_surface.blit(sprite.image, sprite.rect.topleft - self.offset)
