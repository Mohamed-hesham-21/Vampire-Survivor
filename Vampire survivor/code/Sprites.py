from typing import Any
import math
import random
import collections
from settings import *
from math import atan2, degrees


# =============================================================================
# MOVEMENT ALGORITHM CONFIGURATION
# =============================================================================
# 0: Stationary (Enemies do not move at all)
# 1: Random Movement
# 2: Direct Line-of-sight Tracking (Original)
# 3: Individual BFS Per Enemy (Throttled with 0.3s timer)
# 4: BFS from Player to All Tiles (Recalculated every frame)
# 5: Optimized BFS (Cached Flow Field - recalculates only when player changes tile)
# 6: Real-Time Heavy BFS (Per enemy every frame until player found - Lag Demo)
MOVEMENT_MODE = 0


# -----------------------------------------------------------------------------
# BFS Pathfinding Helpers (Used by Modes 3, 4, 5, and 6)
# -----------------------------------------------------------------------------
_BLOCKED_TILES = None

def get_blocked_tiles(collision_sprites):
    """Generates and caches the set of blocked (x, y) tile coordinates."""
    global _BLOCKED_TILES
    if _BLOCKED_TILES is None:
        _BLOCKED_TILES = set()
        # Map boundaries (52x50 tiles)
        for y in range(50):
            for x in range(52):
                tile_box = pygame.Rect(x * TILE_SIZE + 14, y * TILE_SIZE + 14, 36, 36)
                for sprite in collision_sprites:
                    if sprite.rect.colliderect(tile_box):
                        _BLOCKED_TILES.add((x, y))
                        break
    return _BLOCKED_TILES

def get_neighbors(tile, blocked):
    """Yields walkable orthogonal neighbors (Up, Down, Left, Right)."""
    x, y = tile
    for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0)):
        nx, ny = x + dx, y + dy
        if 0 <= nx < 52 and 0 <= ny < 50 and (nx, ny) not in blocked:
            yield (nx, ny)

def find_nearest_walkable(tile, blocked):
    """If a tile is blocked, finds the closest walkable tile via BFS ring."""
    if tile not in blocked and 0 <= tile[0] < 52 and 0 <= tile[1] < 50:
        return tile
    visited = {tile}
    queue = collections.deque([tile])
    while queue:
        cx, cy = queue.popleft()
        for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)):
            nxt = (cx + dx, cy + dy)
            if 0 <= nxt[0] < 52 and 0 <= nxt[1] < 50 and nxt not in visited:
                if nxt not in blocked:
                    return nxt
                visited.add(nxt)
                queue.append(nxt)
    return tile

def bfs_path(start, goal, blocked):
    """
    Standard BFS starting at 'start' and expanding outward until 'goal' (Player)
    is found. Backtracks and returns the shortest path as a list of tiles.
    """
    start = find_nearest_walkable(start, blocked)
    goal = find_nearest_walkable(goal, blocked)
    if start == goal:
        return []

    queue = collections.deque([start])
    came_from = {start: None}

    while queue:
        current = queue.popleft()
        # Early exit as soon as the player is found!
        if current == goal:
            break
        for nxt in get_neighbors(current, blocked):
            if nxt not in came_from:
                came_from[nxt] = current
                queue.append(nxt)

    if goal not in came_from:
        return []

    path = []
    curr = goal
    while curr != start:
        path.append(curr)
        curr = came_from[curr]
    path.reverse()
    return path

def bfs_flow_field(target, blocked):
    """Modes 4 & 5: Reverse BFS from target to all reachable tiles in map."""
    target = find_nearest_walkable(target, blocked)
    queue = collections.deque([target])
    next_step = {target: target}

    while queue:
        current = queue.popleft()
        for nxt in get_neighbors(current, blocked):
            if nxt not in next_step:
                next_step[nxt] = current
                queue.append(nxt)
    return next_step


# -----------------------------------------------------------------------------
# Game Sprites
# -----------------------------------------------------------------------------
class Tiles(pygame.sprite.Sprite):
    def __init__(self, image, pos, group):
        super().__init__(group)
        self.image = image
        self.rect = self.image.get_frect(topleft = pos)
        self.ground = True

class Collision_sprite(pygame.sprite.Sprite):
    def __init__(self, image, pos, group):
        super().__init__(group)
        self.image = image
        self.rect = self.image.get_frect(topleft = pos)

class Gun(pygame.sprite.Sprite):
    def __init__(self, player, group):
        self.player = player
        self.distance = 150
        self.player_direction = pygame.Vector2(1, 0)

        super().__init__(group)
        self.image = pygame.image.load('images/gun/gun.png').convert_alpha()
        self.original_image = self.image
        self.rect = self.image.get_frect(center = self.player.rect.center + self.player_direction * self.distance)
    
    def get_direction(self):
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
        player_pos = pygame.Vector2(WORLD_WIDTH / 2, WORLD_HEIGHT / 2)
        direction = mouse_pos - player_pos
        if direction.length() > 0:
            self.player_direction = direction.normalize()
    
    def rotate_gun(self):
        angle = (degrees(atan2(self.player_direction.x, self.player_direction.y)) - 90)
        self.image = pygame.transform.rotate(self.original_image, angle)
        if self.player_direction.x < 0:
            self.image = pygame.transform.rotate(self.original_image, abs(angle))
            self.image = pygame.transform.flip(self.image, False, True)

    def update(self, _):
        self.get_direction()
        self.rotate_gun()
        self.rect.center = self.player.rect.center + self.player_direction * self.distance

class Bullet(pygame.sprite.Sprite):
    def __init__(self, surf, pos, direction, group):
        super().__init__(group)
        self.image = surf
        self.rect = self.image.get_frect(center = pos)
        
        self.timer = pygame.time.get_ticks()
        self.life_time = 3000

        self.direction = direction
        self.speed = 600

    def update(self, dt):
        self.rect.center += self.direction * self.speed * dt
        if pygame.time.get_ticks() - self.timer > self.life_time:
            self.kill()

class Enemy(pygame.sprite.Sprite):
    # Class-level cache for Flow Field (Modes 4 & 5)
    cached_flow_field = None
    last_player_tile = None
    last_frame_ticks = -1

    def __init__(self, pos, frames, groups, player, collision_sprites, game=None):
        super().__init__(groups)
        self.player = player
        self.game = game
        
        self.frames, self.curr_index = frames, 0
        self.image = self.frames[0]
        self.rect = self.image.get_frect(topleft = pos)
        
        self.animation_speed = 6
        # Optimized hitbox so enemy body (~58px) can fit through 64px tiles without snagging
        self.hit_box = self.rect.inflate(-70, -30)
        self.collision_sprites = collision_sprites
        
        self.speed = 200
        self.direction = pygame.Vector2()

        self.death_timer = 0
        self.death_duration = 400

        # Mode 1 (Random) timer
        self.random_timer = 0.0
        self.random_interval = random.uniform(1.0, 2.0)

        # Mode 3 (Individual BFS) path
        self.bfs_path = []
        self.bfs_timer = 0.0
        self.bfs_interval = 0.3

        # Safety check: if spawned inside an obstacle, push to nearest open tile
        blocked = get_blocked_tiles(self.collision_sprites)
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.hit_box):
                walkable = find_nearest_walkable(self.tile_pos, blocked)
                self.hit_box.center = (walkable[0] * TILE_SIZE + 32, walkable[1] * TILE_SIZE + 32)
                self.rect.center = self.hit_box.center
                break

    @property
    def tile_pos(self) -> tuple[int, int]:
        return (int(self.rect.centerx // TILE_SIZE), int(self.rect.centery // TILE_SIZE))

    @property
    def player_tile_pos(self) -> tuple[int, int]:
        return (int(self.player.rect.centerx // TILE_SIZE), int(self.player.rect.centery // TILE_SIZE))

    # =========================================================================
    # THE 7 MOVEMENT FUNCTIONS (0 to 6)
    # =========================================================================

    def move_stationary(self, dt):
        """0. Stationary mode: monsters stay completely still."""
        self.direction = pygame.Vector2(0, 0)

    def move_random(self, dt):
        """1. Monsters pick a random direction and wander around."""
        self.random_timer += dt
        if self.random_timer >= self.random_interval or self.direction.length() == 0:
            self.random_timer = 0.0
            self.random_interval = random.uniform(1.0, 2.0)
            angle = random.uniform(0, 2 * math.pi)
            self.direction = pygame.Vector2(math.cos(angle), math.sin(angle))

    def move_direct(self, dt):
        """2. The original movement: direct line-of-sight vector to player."""
        player_pos = pygame.Vector2(self.player.rect.center)
        enemy_pos = pygame.Vector2(self.rect.center)
        direction = player_pos - enemy_pos
        if direction.length() > 0:
            self.direction = direction.normalize()
        else:
            self.direction = pygame.Vector2()

    def move_individual_bfs(self, dt):
        """3. Every enemy independently runs BFS with a 0.3s throttle timer."""
        self.bfs_timer += dt
        blocked = get_blocked_tiles(self.collision_sprites)

        if self.bfs_timer >= self.bfs_interval or not self.bfs_path:
            self.bfs_timer = 0.0
            self.bfs_path = bfs_path(self.tile_pos, self.player_tile_pos, blocked)

        if self.bfs_path:
            target_tile = self.bfs_path[0]
            target_pos = pygame.Vector2(target_tile[0] * TILE_SIZE + 32, target_tile[1] * TILE_SIZE + 32)
            dist_vec = target_pos - pygame.Vector2(self.rect.center)

            if dist_vec.length() < 24:
                self.bfs_path.pop(0)
                if self.bfs_path:
                    next_tile = self.bfs_path[0]
                    target_pos = pygame.Vector2(next_tile[0] * TILE_SIZE + 32, next_tile[1] * TILE_SIZE + 32)
                    dist_vec = target_pos - pygame.Vector2(self.rect.center)

            if dist_vec.length() > 0:
                self.direction = dist_vec.normalize()
        else:
            self.move_direct(dt)

    def move_player_flowfield(self, dt):
        """4. Reverse BFS from player to all tiles, recomputed EVERY frame."""
        ticks = pygame.time.get_ticks()
        # Recalculate once per frame for all enemies
        if ticks != Enemy.last_frame_ticks:
            Enemy.last_frame_ticks = ticks
            blocked = get_blocked_tiles(self.collision_sprites)
            Enemy.cached_flow_field = bfs_flow_field(self.player_tile_pos, blocked)

        self._follow_flow_field()

    def move_optimized_bfs(self, dt):
        """5. Optimized BFS: only recalculates when the player moves to a NEW tile!"""
        curr_player_tile = self.player_tile_pos
        if curr_player_tile != Enemy.last_player_tile or Enemy.cached_flow_field is None:
            Enemy.last_player_tile = curr_player_tile
            blocked = get_blocked_tiles(self.collision_sprites)
            Enemy.cached_flow_field = bfs_flow_field(curr_player_tile, blocked)

        self._follow_flow_field()

    def move_heavy_bfs(self, dt):
        """
        6. Real-Time Heavy BFS (Every Frame Per Enemy):
        Runs a fresh queue-based BFS expanding from this enemy's tile UNTIL
        the player's tile is reached, with ZERO caching or timers.
        Demonstrates the massive CPU lag of per-frame un-optimized graph search.
        """
        blocked = get_blocked_tiles(self.collision_sprites)
        # Fresh BFS search executed directly this frame
        path = bfs_path(self.tile_pos, self.player_tile_pos, blocked)

        if path:
            target_tile = path[0]
            target_pos = pygame.Vector2(target_tile[0] * TILE_SIZE + 32, target_tile[1] * TILE_SIZE + 32)
            dist_vec = target_pos - pygame.Vector2(self.rect.center)
            if dist_vec.length() > 0:
                self.direction = dist_vec.normalize()
        else:
            self.move_direct(dt)

    def _follow_flow_field(self):
        """Helper to sample movement direction from the flow field."""
        flow = Enemy.cached_flow_field
        curr_tile = self.tile_pos

        if flow and curr_tile in flow:
            next_tile = flow[curr_tile]
        elif flow:
            blocked = get_blocked_tiles(self.collision_sprites)
            nearest = find_nearest_walkable(curr_tile, blocked)
            next_tile = flow.get(nearest, curr_tile)
        else:
            self.move_direct(0)
            return

        if next_tile == curr_tile:
            self.move_direct(0)
        else:
            target_pos = pygame.Vector2(next_tile[0] * TILE_SIZE + 32, next_tile[1] * TILE_SIZE + 32)
            dist_vec = target_pos - pygame.Vector2(self.rect.center)
            if dist_vec.length() > 0:
                self.direction = dist_vec.normalize()

    # =========================================================================
    # MAIN MOVE FUNCTION
    # =========================================================================
    def move(self, dt):
        # 1. Determine active movement mode
        if self.game is not None and hasattr(self.game, 'movement_mode'):
            mode = self.game.movement_mode
        else:
            mode = MOVEMENT_MODE

        # 2. Call the chosen movement algorithm
        if mode == 0:
            self.move_stationary(dt)
            return
        elif mode == 1:
            self.move_random(dt)
        elif mode == 2:
            self.move_direct(dt)
        elif mode == 3:
            self.move_individual_bfs(dt)
        elif mode == 4:
            self.move_player_flowfield(dt)
        elif mode == 5:
            self.move_optimized_bfs(dt)
        elif mode == 6:
            self.move_heavy_bfs(dt)

        # 3. Update position and handle collisions with smooth axis sliding
        self.hit_box.x += self.direction.x * self.speed * dt
        self.collision(0, dt)
        self.hit_box.y += self.direction.y * self.speed * dt
        self.collision(1, dt)

        self.rect.center = self.hit_box.center

    def collision(self, dimension, dt):
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.hit_box):
                if not dimension:
                    if self.direction.x > 0:
                        self.hit_box.right = sprite.rect.left
                    elif self.direction.x < 0:
                        self.hit_box.left = sprite.rect.right
                else:
                    if self.direction.y > 0:
                        self.hit_box.bottom = sprite.rect.top
                    elif self.direction.y < 0:
                        self.hit_box.top = sprite.rect.bottom

                if (self.game.movement_mode if self.game else MOVEMENT_MODE) == 1:
                    self.random_timer = self.random_interval
                return

    def destroy(self):
        self.death_timer = pygame.time.get_ticks()
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
        else:
            self.death_time()
