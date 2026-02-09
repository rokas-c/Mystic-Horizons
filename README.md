# Mystic Horizons

A 2D fantasy platformer developed using Python and the Pygame library. The project focuses on implementing core game engine mechanics, including parallax rendering, state-based AI, and physics-based character controllers.

## Technical Features

* **Parallax Scrolling System:** Engineered a multi-layered background rendering engine with 6 independent layers to create a pseudo-3D depth effect.
* **State-Driven AI:** Implemented an automated enemy system (Crow) featuring patrol, chase, and combat states with dynamic health management.
* **Physics & Collision:** Developed a custom gravity-based movement controller and platform collision detection using AABB (Axis-Aligned Bounding Box) logic.
* **Animation Pipeline:** Built a frame-based animation system that handles transitions between Idle, Walk, Jump, and Attack states based on player input and velocity.
* **Game State Management:** Programmed a centralized game loop managing transitions between Main Menu, active gameplay, and Game Over states.

## Tech Stack

* **Language:** Python
* **Library:** Pygame
* **Methodology:** Object-Oriented Programming (OOP)

## Installation & Execution

1. Ensure Python 3.x is installed on your system.
2. Install the required dependency:
   ```bash
   pip install pygame
