from typing import Any
from settings import *
from math import atan2 , degrees
class Tiles(pygame.sprite.Sprite):
    def __init__(self,image , pos ,  group):
        super().__init__(group)
        self.image = image
        self.rect = self.image.get_frect(topleft = pos)
        self.ground = True
class Collision_sprite(pygame.sprite.Sprite):
    def __init__(self,image , pos ,  group):
        super().__init__(group)
        self.image = image
        self.rect = self.image.get_frect(topleft = pos)
class Gun(pygame.sprite.Sprite):
    def __init__(self, player, group):
        
        # player connection
        self.player = player
        self.distance = 150
        self.player_direction = pygame.Vector2(1, 0)

        # sprite setup
        super().__init__(group)
        self.image = pygame.image.load('images/gun/gun.png').convert_alpha()
        self.original_image = self.image
        self.rect = self.image.get_frect(center = self.player.rect.center + self.player_direction * self.distance)
    
    def get_direction(self):
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
        player_pos = pygame.Vector2(WORLD_WIDTH / 2,WORLD_HEIGHT / 2)
        self.player_direction = (mouse_pos - player_pos).normalize() 
    
    def rotate_gun(self):
        angle = (degrees(atan2(self.player_direction.x, self.player_direction.y)) - 90)
        self.image = pygame.transform.rotate(self.original_image, angle)
        if self.player_direction.x < 0 :
            self.image = pygame.transform.rotate(self.original_image, abs(angle))
            self.image = pygame.transform.flip(self.image, False, True)
    def update(self,_):
        self.get_direction()
        self.rotate_gun()
        self.rect.center = self.player.rect.center + self.player_direction * self.distance

class Bullet(pygame.sprite.Sprite):
    def __init__(self, surf, pos, direction, group):
        super().__init__(group)
        self.image = surf
        self.rect = self.image.get_frect(center = pos)
        
        self.timer = pygame.time.get_ticks()
        self.life_time = 3000  # milliseconds

        self.direction = direction
        self.speed = 600
    def update(self, dt):
        self.rect.center += self.direction * self.speed * dt
        if pygame.time.get_ticks() - self.timer > self.life_time:
            self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, frames, groups, player, collision_sprites):
        super().__init__(groups)
        self.player = player
        
        self.frames, self.curr_index = frames, 0
        self.image = self.frames[0]
        self.rect = self.image.get_frect(topleft = pos)
        
        self.animation_speed = 6
        self.hit_box = self.rect.inflate(-20, -40)
        self.collision_sprites = collision_sprites
        
        self.speed = 200
        self.direction = pygame.Vector2()

        self.death_timer = 0
        self.death_duration = 400
    
    def move(self, dt):
        # get direction
        player_pos = pygame.Vector2(self.player.rect.center)
        enemy_pos = pygame.Vector2(self.rect.center)
        self.direction = (player_pos - enemy_pos).normalize()
        

        #update rect position + collision
        self.hit_box.x += self.direction.x * self.speed * dt
        self.collision(0, dt)
        self.hit_box.y += self.direction.y * self.speed * dt
        self.collision(1, dt)

        self.rect.center = self.hit_box.center

    def collision(self, dimension , dt):
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.hit_box):
                if not dimension : # x axis collision
                    if self.direction.x > 0 : # player moving right
                        self.hit_box.right = sprite.rect.left
                    elif self.direction.x < 0 : # player moving left
                        self.hit_box.left = sprite.rect.right

                else : # y axis collision
                    if self.direction.y > 0 : # player moving down
                        self.hit_box.bottom = sprite.rect.top
                    elif self.direction.y < 0 : # player moving up
                        self.hit_box.top = sprite.rect.bottom
                return

    def destroy(self):
        # set a timer
        self.death_timer = pygame.time.get_ticks()
        # change image
        surf = pygame.mask.from_surface(self.frames[0]).to_surface()
        surf.set_colorkey('black')
        self.image = surf

    def animate(self, dt):
        self.curr_index += dt * self.animation_speed
        self.curr_index %= len(self.frames)
        self.image = self.frames[int(self.curr_index)]
    
    def death_time(self):
        if pygame.time.get_ticks() - self.death_timer >= self.death_duration:
            self.kill()
    def update(self, dt):
        if self.death_timer == 0:
            self.move(dt)
            self.animate(dt)
        else :
            self.death_time()