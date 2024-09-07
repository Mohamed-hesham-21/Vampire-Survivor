from settings import *

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, group, collision_sprites ):
        super().__init__(group)
        self.image = pygame.image.load('images/player/down/0.png')
        self.rect = self.image.get_frect(center = pos)
        self.collision_sprites = collision_sprites
        self.hit_box = self.rect.inflate(-60 , -90)
        
        self.frame_state, self.frame_index = 'down' , 0
        self.get_frames()
        # movement
        self.direction = pygame.Vector2()
        self.speed = 500

    def get_frames(self):
        self.frames = {
            'down' : [],
            'left' : [],
            'right' : [],
            'up' : []
        }

        for state in self.frames:
            for full_path, folder_name, file_names in walk(f'images/player/{state}'):
                for file_name in sorted(file_names , key = lambda file : file[0]):
                    self.frames[state].append(pygame.image.load(str(full_path +'/'+ file_name)).convert_alpha())
    def animation(self, dt):
        # get state
        if self.direction.x !=0 :
            self.frame_state = 'right' if self.direction.x > 0  else 'left'
        if self.direction.y !=0 :
            self.frame_state = 'up' if self.direction.y < 0  else 'down'
        
        
        # Animate   
        self.frame_index = dt * 5 + self.frame_index if self.direction else 0 
        self.frame_index %= len(self.frames[self.frame_state])
        self.image = self.frames[self.frame_state][int(self.frame_index)]

    def input(self):
        keys = pygame.key.get_pressed()
        self.direction = pygame.Vector2(int(keys[pygame.K_RIGHT] or keys[pygame.K_d]) - int(keys[pygame.K_LEFT] or keys[pygame.K_a]),
        int(keys[pygame.K_DOWN] or keys[pygame.K_s]) - int(keys[pygame.K_UP] or keys[pygame.K_w]))
        self.direction = self.direction.normalize() if self.direction else self.direction

    def move(self, dt):
        dimension = 0
        self.hit_box.x += self.direction.x * dt * self.speed
        self.collision(dimension, dt)
        dimension += 1
        self.hit_box.y += self.direction.y * dt * self.speed
        self.collision(dimension, dt)
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
    
    def update(self , dt):
        self.input()
        self.move(dt)
        self.animation(dt)

