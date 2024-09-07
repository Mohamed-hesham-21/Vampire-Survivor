from settings import *
from Player import Player
from Sprites import *
from Groups import All_Sprites
from random import randint, choice
from pytmx.util_pygame import load_pygame


class Game():
    def __init__(self):
        pygame.init()
        
        # Initialize the game
        self.screen = pygame.display.set_mode((WORLD_WIDTH, WORLD_HEIGHT))
        pygame.display.set_caption('Vampire Survivor')
        self.clock = pygame.time.Clock()
        self.running = True

        # Groups
        self.all_sprites = All_Sprites()
        self.collision_sprites = pygame.sprite.Group()
        self.Bullets_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()
        

        # gun timer
        self.gun_timer = -1000
        self.gun_cooldown = 100

        # spawn timer 
        self.enemy_event = pygame.event.custom_type()
        pygame.time.set_timer(self.enemy_event, 300)
        self.enemy_position = []
        
        self.setup()

    def load_images(self):
        self.Bullet_surf = pygame.image.load('images/gun/bullet.png').convert_alpha()
        folders = list(walk('images/enemies'))[0][1]
        
        self.enemy_frames = {}
        for folder in folders:
            for full_path, _, file_names in walk('images/enemies' + '/' + folder):
                self.enemy_frames[folder] = []
                for file in sorted(file_names, key=lambda x: int(x[0])):
                    self.enemy_frames[folder].append(pygame.image.load('images/enemies/'+ folder + '/' + file).convert_alpha())

    def load_sounds(self):
        self.gun_sound = pygame.mixer.Sound('audio/shoot.wav')
        self.world_music = pygame.mixer.Sound('audio/music.wav')
        self.impact_sound = pygame.mixer.Sound('audio/impact.ogg')
    def setup(self):
        self.load_images()
        self.load_sounds()
        self.map = load_pygame('data/maps/world.tmx')
        for x , y , image in self.map.get_layer_by_name('Ground').tiles():
            Tiles(image, (x * TILE_SIZE, y * TILE_SIZE), (self.all_sprites))
        
        for obj in self.map.get_layer_by_name('Collisions'):
            Collision_sprite(pygame.Surface((obj.width , obj.height)), (obj.x, obj.y),  self.collision_sprites)

        for object in self.map.get_layer_by_name('Objects') :
            Collision_sprite(object.image, (object.x, object.y), (self.all_sprites, self.collision_sprites))

        for marker in self.map.get_layer_by_name('Entities'):
            if marker.name == 'Player':
                self.player = Player((marker.x , marker.y), self.all_sprites, self.collision_sprites)
                self.gun = Gun(self.player, self.all_sprites)
            elif marker.name == 'Enemy':
                self.enemy_position.append((marker.x, marker.y))
        self.world_music.play(-1)

    def get_input(self):
        if pygame.mouse.get_just_pressed()[0] and pygame.time.get_ticks()  - self.gun_timer >= self.gun_cooldown:
            self.gun_sound.play()
            pos = self.gun.rect.center + self.gun.player_direction * 50
            Bullet(self.Bullet_surf, pos, self.gun.player_direction, (self.all_sprites, self.Bullets_sprites))
            self.gun_timer = pygame.time.get_ticks()
        
    def player_collision(self):
        if pygame.sprite.spritecollide(self.player, self.enemy_sprites, True, pygame.sprite.collide_mask):
            self.player.destroy()
            self.running = False
    def bullet_collision(self):
        for bullet in self.Bullets_sprites:
            collision_sprites =  pygame.sprite.spritecollide(bullet, self.enemy_sprites, False, pygame.sprite.collide_mask)
            if collision_sprites:
                self.impact_sound.play()
                for sprite in collision_sprites:
                    sprite.destroy()
                bullet.kill()
    def run(self):
        while self.running:
            # dt
            dt = self.clock.tick() / 1000
            
            # handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == self.enemy_event:
                    Enemy(choice(self.enemy_position), choice(list(self.enemy_frames.values())), (self.all_sprites, self.enemy_sprites), self.player, self.collision_sprites)
            
            # update
            
            self.get_input()
            self.player_collision()
            self.bullet_collision()
            self.all_sprites.update(dt)
            self.screen.fill((0, 0, 0))
            
            # draw
            self.all_sprites.draw(self.player.rect.center)
            pygame.display.update()
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()
