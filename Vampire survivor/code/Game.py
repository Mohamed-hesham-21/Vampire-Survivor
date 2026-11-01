from settings import *
from Player import Player
from Sprites import *
from Groups import All_Sprites
from random import randint, choice
from pytmx.util_pygame import load_pygame
import os


# =============================================================================
# CONFIGURATION: DEMO MODE vs SINGLE ALGORITHM MODE
# =============================================================================
# Set to True  -> Interactive Demo Mode:
#                 - Keys [0-6] switch algorithms in real-time during gameplay
#                 - Shows on-screen HUD with active algorithm and live FPS
# Set to False -> Single Algorithm Mode:
#                 - Runs ONLY the chosen ACTIVE_ALGORITHM for the whole game
#                 - Disables key switching
#                 - HIDES the FPS counter and demo HUD completely
DEMO_MODE = True

# Choose which algorithm runs (0 to 6):
# 0: Stationary (Enemies do not move at all)
# 1: Random Movement
# 2: Direct Line-of-sight Tracking (Original)
# 3: Individual BFS Per Enemy (Throttled with 0.3s timer)
# 4: Full BFS Every Frame (Single reverse BFS from player to all tiles)
# 5: Optimized BFS (Cached Flow Field - recalculates only on new player tile)
# 6: Real-Time Heavy BFS (Per enemy every frame until player found - Lag Demo)
ACTIVE_ALGORITHM = 6


class Game():
    def __init__(self, demo_mode=DEMO_MODE, active_algorithm=ACTIVE_ALGORITHM):
        pygame.init()
        
        # Initialize the game
        self.screen = pygame.display.set_mode((WORLD_WIDTH, WORLD_HEIGHT))
        pygame.display.set_caption('Vampire Survivor')
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_over = False

        # Demo mode vs Single algorithm mode
        self.demo_mode = demo_mode
        self.movement_mode = active_algorithm

        # Sync with Sprites.MOVEMENT_MODE
        import Sprites
        Sprites.MOVEMENT_MODE = active_algorithm

        # HUD Fonts
        self.hud_font = pygame.font.Font(None, 24)
        self.info_font = pygame.font.Font(None, 22)

        self.mode_names = {
            0: "0: Still",
            1: "1: Random",
            2: "2: Direct",
            3: "3: BFS (0.3s)",
            4: "4: Full BFS",
            5: "5: Opt BFS",
            6: "6: Heavy BFS"
        }

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

    # -------------------------------------------------------------------------
    # Explicit Mode Switch Functions (can be called programmatically)
    # -------------------------------------------------------------------------
    def set_mode_stationary(self):
        """Switches movement to Stationary (Mode 0 - enemies do not move)."""
        self.set_movement_mode(0)

    def set_mode_random(self):
        """Switches movement to Random Movement (Mode 1)."""
        self.set_movement_mode(1)

    def set_mode_direct(self):
        """Switches movement to Direct Line-of-Sight Tracking (Mode 2)."""
        self.set_movement_mode(2)

    def set_mode_individual_bfs(self):
        """Switches movement to Individual BFS Per Enemy with 0.3s timer (Mode 3)."""
        self.set_movement_mode(3)

    def set_mode_player_flowfield(self):
        """Switches movement to Player Reverse BFS Every Frame (Mode 4)."""
        self.set_movement_mode(4)

    def set_mode_optimized_bfs(self):
        """Switches movement to Optimized Cached Reverse BFS (Mode 5)."""
        self.set_movement_mode(5)

    def set_mode_heavy_bfs(self):
        """Switches movement to Real-Time Heavy BFS every frame per enemy (Mode 6)."""
        self.set_movement_mode(6)

    def set_movement_mode(self, mode: int):
        """Changes the active algorithm mode (0 to 6)."""
        self.movement_mode = mode
        import Sprites
        Sprites.MOVEMENT_MODE = mode

        # Reset cached flow fields and paths when switching
        Enemy.cached_flow_field = None
        Enemy.last_player_tile = None
        Enemy.last_frame_ticks = -1
        for enemy in self.enemy_sprites:
            if hasattr(enemy, 'bfs_path'):
                enemy.bfs_path.clear()
            if mode == 0:
                enemy.direction = pygame.Vector2(0, 0)

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

        for x, y, image in self.map.get_layer_by_name('Ground').tiles():
            Tiles(image, (x * TILE_SIZE, y * TILE_SIZE), (self.all_sprites))
        
        for obj in self.map.get_layer_by_name('Collisions'):
            Collision_sprite(pygame.Surface((obj.width, obj.height)), (obj.x, obj.y), self.collision_sprites)

        for object in self.map.get_layer_by_name('Objects'):
            Collision_sprite(object.image, (object.x, object.y), (self.all_sprites, self.collision_sprites))

        for marker in self.map.get_layer_by_name('Entities'):
            if marker.name == 'Player':
                self.player = Player((marker.x, marker.y), self.all_sprites, self.collision_sprites)
                self.gun = Gun(self.player, self.all_sprites)
            elif marker.name == 'Enemy':
                self.enemy_position.append((marker.x, marker.y))
        self.world_music.play(-1)

    def get_input(self):
        if pygame.mouse.get_pressed()[0] and pygame.time.get_ticks() - self.gun_timer >= self.gun_cooldown:
            self.gun_sound.play()
            pos = self.gun.rect.center + self.gun.player_direction * 50
            Bullet(self.Bullet_surf, pos, self.gun.player_direction, (self.all_sprites, self.Bullets_sprites))
            self.gun_timer = pygame.time.get_ticks()
        
    def player_collision(self):
        for enemy in self.enemy_sprites:
            # 1. Ignore dead enemies in death animation
            if enemy.death_timer == 0:
                # 2. Check actual physical body hit_boxes (prevents phantom hits through trees)
                if self.player.hit_box.colliderect(enemy.hit_box):
                    self.player.destroy()
                    self.game_over = True
                    pygame.time.set_timer(self.enemy_event, 0)  # stop spawning enemies
                    break
            
    def bullet_collision(self):
        for bullet in self.Bullets_sprites:
            collision_sprites = pygame.sprite.spritecollide(bullet, self.enemy_sprites, False, pygame.sprite.collide_mask)
            if collision_sprites:
                self.impact_sound.play()
                for sprite in collision_sprites:
                    if sprite.death_timer == 0:
                        sprite.destroy()
                bullet.kill()

    def draw_hud(self):
        """Draws top HUD banner only when DEMO_MODE is True. Hidden in single mode."""
        if not self.demo_mode:
            return  # No HUD, NO FPS shown in single algorithm mode!

        panel = pygame.Surface((WORLD_WIDTH, 68), pygame.SRCALPHA)
        panel.fill((20, 20, 30, 210))
        self.screen.blit(panel, (0, 0))

        # Mode names [0] through [6] with active one highlighted in gold
        x_offset = 12
        for mode_num in range(7):
            name = self.mode_names[mode_num]
            if mode_num == self.movement_mode:
                color = (255, 215, 0)
                display_text = f"[{name}]"
            else:
                color = (170, 170, 180)
                display_text = f" {mode_num} "

            surf = self.hud_font.render(display_text, True, color)
            self.screen.blit(surf, (x_offset, 10))
            x_offset += surf.get_width() + 14

        # Live FPS and enemy count
        fps = self.clock.get_fps()
        fps_color = (0, 255, 120) if fps >= 55 else (255, 180, 0) if fps >= 30 else (255, 60, 60)
        perf_text = f"Press [0-6] to Switch Mode  |  FPS: {fps:.1f}  |  Enemies: {len(self.enemy_sprites)}"
        info_surf = self.info_font.render(perf_text, True, fps_color)
        self.screen.blit(info_surf, (12, 40))

    def run(self):
        while self.running:
            # dt
            dt = self.clock.tick() / 1000
            
            # handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    # Hotkeys 0-6 active in Demo Mode
                    elif self.demo_mode:
                        if event.key == pygame.K_0:
                            self.set_mode_stationary()
                        elif event.key == pygame.K_1:
                            self.set_mode_random()
                        elif event.key == pygame.K_2:
                            self.set_mode_direct()
                        elif event.key == pygame.K_3:
                            self.set_mode_individual_bfs()
                        elif event.key == pygame.K_4:
                            self.set_mode_player_flowfield()
                        elif event.key == pygame.K_5:
                            self.set_mode_optimized_bfs()
                        elif event.key == pygame.K_6:
                            self.set_mode_heavy_bfs()

                if not self.game_over and event.type == self.enemy_event:
                    Enemy(
                        choice(self.enemy_position),
                        choice(list(self.enemy_frames.values())),
                        (self.all_sprites, self.enemy_sprites),
                        self.player,
                        self.collision_sprites,
                        game=self
                    )
            
            if not self.game_over:
                # update
                self.get_input()
                self.player_collision()
                self.bullet_collision()
                self.all_sprites.update(dt)

            self.screen.fill((0, 0, 0))
            
            # draw
            self.all_sprites.draw(self.player.rect.center)

            # draw HUD (only draws if demo_mode is True)
            self.draw_hud()

            if self.game_over:
                # draw game over text
                font = pygame.font.Font(None, 74)
                text = font.render('GAME OVER', True, (255, 0, 0))
                text_rect = text.get_rect(center = (WORLD_WIDTH / 2, WORLD_HEIGHT / 2 - 40))
                self.screen.blit(text, text_rect)

                hint_font = pygame.font.Font(None, 36)
                hint = hint_font.render('Press ESC to quit', True, (255, 255, 255))
                hint_rect = hint.get_rect(center = (WORLD_WIDTH / 2, WORLD_HEIGHT / 2 + 20))
                self.screen.blit(hint, hint_rect)

            pygame.display.update()
        pygame.quit()

if __name__ == "__main__":
    os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
    game = Game()
    game.run()
