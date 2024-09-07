# Vampire Survivors 2D Game (Pygame)

Welcome to **Vampire Survivors**, a 2D game developed using Pygame. In this game, players control a character to survive waves of enemies for as long as possible. The game features smooth animation, dynamic enemy spawning, and collision mechanics.

---

## Table of Contents
- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
  - [Requirements](#requirements)
  - [Clone the Repository](#clone-the-repository)
  - [Running the Game](#running-the-game)
- [How to Play](#how-to-play)
  - [Controls](#controls)
- [Game Files](#game-files)
- [Benefits of Developing this Game](#benefits-of-developing-this-game)
- [Acknowledgements](#acknowledgements)
- [Contributing](#contributing)


## Introduction
This game is the second game in [Clear Code](https://youtu.be/8OMghdHP-zs?si=VKX6-PRyyGkbAQxd)'s video and inspired by the popular "Vampire Survivors" genre. The player must dodge and defeat waves of enemies to survive for as long as possible. The game includes player movement, enemy behavior, and collision detection for an immersive survival experience.

## Features
- **Multiple enemies** with different behaviors and animations
- **Collision detection** for player-enemy and environmental interactions
- **High score tracking**
- **Simple controls** for easy-to-learn gameplay
- **Smooth animations** and dynamic enemy spawning

## Installation
Follow these steps to install and run the game on your local machine:

### Requirements
- **Python 3.x** (Download [here](https://www.python.org/downloads/))
- **Pygame** library (Install using the command below)

```bash
pip install pygame
```

### Clone the Repository
```bash
git clone https://github.com/yourusername/vampire-survivors-game.git
cd vampire-survivors-game
```

### Running the Game
Once you've installed the dependencies, you can run the game by executing the following command:

```bash
python Game.py
```

## How to Play
- **Controls**: Use the arrow keys or WASD to move your character.
- **Objective**: Survive as long as you can by defeating enemies and avoiding getting touched!.

### Controls:
- **Arrow Keys / WASD**: Move your character
- **Mouse Click**: Select options in the menu

## Game Files

| File/Folder          | Description                                                  |
|----------------------|--------------------------------------------------------------|
| `Game.py`            | The main game file that initializes the game and manages the game loop. |
| `Player.py`          | Defines the `Player` class, handling player movement and collisions. |
| `Sprites.py`         | Defines various game objects (enemies, bullets) and how they interact with the player. |
| `Groups.py`          | Contains different sprite groups (e.g., for managing enemies and bullets). |
| `images/`            | Contains images used in the game. |
| `audio/`             | Contains music and sounds used in the game. |
| `data/`              | Contains map and tiles used in the game. |
| `README.md`          | You're reading it! The description and instructions for the project. |


## Benefits of Developing this Game

Creating this 2D game using Pygame has provided several valuable skills and experiences:

### 1. **Improved Game Development Skills**
   - Working on this project has deepened my understanding of **game mechanics**, such as player movement, enemy AI, and collision detection.
   - I have gained practical experience in **game architecture**, organizing the code into classes, handling game states, and using sprite groups effectively.

### 2. **Mastery of Pygame Library**
   - This project strengthened my ability to work with the **Pygame library**, including handling input, rendering images and animations, managing sound effects, and working with sprite-based environments.
   - I learned how to optimize performance, especially when managing multiple sprites on screen and ensuring smooth animations.

### 3. **Problem Solving and Algorithmic Thinking**
   - I improved my ability to solve real-time problems by implementing features like **enemy spawning**, **animation frames**, and **collision detection**.
   - Managing multiple moving objects (player, enemies, bullets) enhanced my understanding of **2D vector math** and **game physics**.

### 4. **Project Management and Version Control**
   - Organizing the project helped me improve my ability to manage codebases, with files dedicated to different game components (player, enemies, game loop, etc.).
   - Using **Git** and **GitHub** allowed me to apply version control and collaborative coding practices, ensuring a smooth development process.

### 5. **Creativity and Design**
   - I got to apply **creativity** in designing characters, choosing enemy behaviors, and crafting a balanced, engaging gameplay experience.
   - Learning to integrate custom **assets** (images, sprites, sounds) gave me insight into game design and asset management.

### 6. **Foundation for Future Projects**
   - This project serves as a **foundation** for future game development efforts, giving me the knowledge and skills to build more complex games with advanced mechanics.
   - It allows for easy expansion, such as adding new levels, enemy types, or multiplayer modes.

Developing this game was both a rewarding challenge and a crucial learning experience, helping me grow as a developer and game designer.


## Acknowledgements

I would like to extend my gratitude to the following resources and communities that made this project possible:

- **[Pygame Documentation](https://www.pygame.org/docs/)**: For providing comprehensive documentation and tutorials that helped me understand how to use the Pygame library effectively.
- **[Real Python](https://realpython.com/)**: For offering beginner-friendly and in-depth tutorials on Python and game development.
- **[Clear Code's YouTube Channel](https://www.youtube.com/c/ClearCode)**: For their insightful Pygame tutorials, which were instrumental in learning game mechanics, animation, and collision handling.
- **[ChatGPT](chatgpt.com)**: A special thanks to **ChatGPT** for helping me write this incredible README! 😊


A special thanks to all the developers and open-source communities who share their knowledge and make learning more accessible!


## Contributing
Contributions are welcome! Please follow these steps to contribute:
1. Fork the repository
2. Create a new branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -m 'Add some new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Open a pull request

