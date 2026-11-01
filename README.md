# Vampire Survivors 2D Game (Pygame-CE) - Pathfinding Algorithms Demo

Welcome to **Vampire Survivors**, a 2D survival game developed using Pygame-CE (Community Edition). Players control a character to survive waves of enemies for as long as possible with smooth animations, dynamic enemy spawning, and an **interactive AI movement & search algorithms comparison engine**.

---

## Table of Contents
- [Introduction](#introduction)
- [Features](#features)
- [Movement & Search Algorithms](#movement--search-algorithms)
  - [The 7 Movement Modes (0 to 6)](#the-7-movement-modes-0-to-6)
  - [Demo Mode vs Single Algorithm Mode](#demo-mode-vs-single-algorithm-mode)
- [Installation](#installation)
  - [Requirements](#requirements)
  - [Clone the Repository](#clone-the-repository)
  - [Set Up the Virtual Environment](#set-up-the-virtual-environment)
  - [Install Dependencies](#install-dependencies)
  - [Running the Game](#running-the-game)
- [How to Play](#how-to-play)
  - [Controls](#controls)
- [Game Files](#game-files)
- [Acknowledgements](#acknowledgements)
- [Contributing](#contributing)

---

## Introduction
This game is inspired by the popular "Vampire Survivors" genre and Clear Code's Pygame tutorials. It includes a built-in comparison engine demonstrating 7 distinct movement modes (0 through 6), allowing you to showcase how different pathfinding techniques affect enemy intelligence, obstacle navigation, and game performance.

## Features
- **7 Real-Time Movement & Search Algorithms (Modes 0 to 6)** for comparative AI analysis
- **Heavy Real-Time BFS Mode (Mode 6)** demonstrating true unthrottled search lag
- **Interactive Demo Mode** with live hotkeys (`0`–`6`) and an on-screen HUD with live FPS
- **Single Algorithm Mode** to lock the game to one specific algorithm and hide the FPS/HUD completely
- **Optimized Collision System**: Physical hitbox detection prevents false game overs through trees
- **Obstacle Navigation**: Enemies properly fit through 64px corridors and avoid getting stuck on map markers
- **Tiled Map (.tmx)** integration with automatic obstacle grid collision detection

---

## Movement & Search Algorithms

### The 7 Movement Modes (0 to 6)

| Mode | Key | Function Call | Algorithm / Technique | Behavior & AI Explanation |
|:---:|:---:|:---|:---|:---|
| **0** | `[0]` | `game.set_mode_stationary()` | **Stationary / Idle** | Monsters stay completely in place and do not move. Perfect baseline for testing shooting, collisions, or spawning. |
| **1** | `[1]` | `game.set_mode_random()` | **Random Walk** | Monsters pick random direction vectors and wander around. When hitting a wall, they bounce off. Demonstrates zero goal-seeking behavior. |
| **2** | `[2]` | `game.set_mode_direct()` | **Direct Vector Tracking (Original)** | Straight line vector: `player_pos - enemy_pos`. Simple and fast, but enemies get permanently stuck behind trees, pillars, and rocks. |
| **3** | `[3]` | `game.set_mode_individual_bfs()` | **Individual BFS (0.3s Timer)** | Each enemy runs its own BFS to find the shortest tile path, throttled with a 0.3s interval to reduce CPU load. |
| **4** | `[4]` | `game.set_mode_player_flowfield()` | **Reverse BFS (Every Frame)** | Runs a full-map BFS flood fill from the player to all tiles every single frame. Enemies sample the gradient vector of their tile. Demonstrates a shared search tree, but recalculating all tiles 60 times/sec in Python wastes CPU. |
| **5** | `[5]` | `game.set_mode_optimized_bfs()` | **Optimized Cached Flow Field** | The reverse BFS is only recalculated when the player actually crosses into a **new grid tile** (event-driven caching). When moving within the same 64x64 tile, cost is 0 ms! Solid 60 FPS even with 100+ enemies navigating obstacles smoothly. |
| **6** | `[6]` | `game.set_mode_heavy_bfs()` | **Real-Time Heavy BFS (Per Enemy/Frame)** | Each enemy runs a fresh unthrottled BFS from its tile **until it finds the player** every single frame. Recalculates 100% from scratch each frame ($O(K \times (V + E))$). Intentionally showcases massive CPU lag and frame drops! |

---

### Demo Mode vs Single Algorithm Mode

At the top of [`Game.py`](file:///d:/pygame/Vampire-Survivor/Vampire%20survivor/code/Game.py#L18), you can easily toggle between the two modes:

```python
# Set to True  -> Interactive Demo Mode: Keys [0-6] switch algorithms in real-time,
#                 shows on-screen HUD with active mode and live FPS.
# Set to False -> Single Algorithm Mode: Runs ONLY the chosen ACTIVE_ALGORITHM,
#                 disables key switching, and HIDES the FPS counter completely.
DEMO_MODE = True

# Choose which algorithm runs (0 to 6):
# 0: Stationary (Enemies do not move at all)
# 1: Random Movement
# 2: Direct Tracking (Original)
# 3: Individual BFS (0.3s Timer)
# 4: Full BFS Every Frame
# 5: Optimized BFS (Cached Flow Field)
# 6: Real-Time Heavy BFS (Lag Demo)
ACTIVE_ALGORITHM = 6
```

---

## Installation
Follow these steps to install and run the game on your local machine:

### Requirements
- **Python 3.12** (Download [here](https://www.python.org/downloads/release/python-31210/))
- **pygame-ce 2.4.1** — the community edition of Pygame
- **pytmx 3.32** — for loading Tiled (.tmx) map files

### Clone the Repository
```bash
git clone https://github.com/yourusername/vampire-survivors-game.git
cd vampire-survivors-game
```

### Set Up the Virtual Environment
Create and activate a virtual environment using Python 3.12:

```bash
# Create the venv
python -m venv venv

# Activate (Windows PowerShell)
venv\Scripts\Activate.ps1

# Activate (Windows CMD)
venv\Scripts\activate.bat

# Activate (macOS / Linux)
source venv/bin/activate
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Running the Game
```bash
cd "Vampire survivor/code"
python Game.py
```

---

## How to Play
- **Arrow Keys / WASD**: Move character
- **Mouse Click**: Shoot bullets towards cursor
- **Keys 0 - 6** *(in Demo Mode)*: Switch movement algorithm in real-time
- **ESC**: Exit the game

---

## Game Files

| File/Folder          | Description                                                  |
|----------------------|--------------------------------------------------------------|
| `Game.py`            | Main game loop, configuration (`DEMO_MODE`), mode switching, HUD, and events. |
| `Sprites.py`         | Contains all 7 movement algorithms, BFS helpers, Enemy, Gun, Bullet. |
| `Player.py`          | Player sprite class, animation, controls, and collisions. |
| `Groups.py`          | Custom camera sprite group managing map offset rendering. |
| `settings.py`        | Constants (world width, height, tile size = 64). |
| `images/`            | Game sprites (player, enemies, gun, bullet). |
| `audio/`             | Sound effects (shoot, impact) and background music. |
| `data/`              | Tiled map files (`world.tmx`) and tileset graphics. |
| `requirements.txt`   | Pinned Python dependencies (`pygame-ce==2.4.1`, `pytmx==3.32`). |
| `README.md`          | Project documentation and setup guide. |

---

## Acknowledgements
- **[Pygame-CE Documentation](https://pyga.me/docs/)**: Community edition reference and docs.
- **[Clear Code's YouTube Channel](https://www.youtube.com/c/ClearCode)**: Original Pygame survival tutorial.
- **[PyTMX](https://github.com/bitcraft/PyTMX)**: Python library for reading TMX map formats.
