Final Project: Mario Game & Watch Recreation
Overview
This repository contains the source code for the Mario Game & Watch final project. This application is a software recreation of the classic handheld console experience, developed using Python and the Pyxel retro game engine.

The project demonstrates proficiency in object-oriented programming (OOP), game loop architecture, and modular software design. It separates game logic, rendering, and entity management into distinct modules to ensure code maintainability and scalability.

Table of Contents
Technical Architecture

Prerequisites

Installation

Usage

Project Structure

Technical Architecture
The application is structured to follow a clear separation of concerns:

Game Logic: Handles the state of the game, score tracking, and collision detection.

Rendering: The renderer.py module is responsible exclusively for drawing sprites and UI elements to the screen, decoupling the visual layer from the logical layer.

Entity Management: Characters and interactive objects are defined as classes in characters.py and entities.py, allowing for easy instantiation and state management.

Prerequisites
To run this project, ensure the following software is installed on your system:

Python 3.8 or higher.

Pyxel: A retro game engine for Python.

Installation
Clone the repository:

Bash

git clone https://github.com/100584680-cell/Final-project-Mario-game-and-watch.git
cd Final-project-Mario-game-and-watch
Install dependencies: The project relies on the Pyxel library. Install it using pip:

Bash

pip install pyxel
Usage
To execute the application, run the entry point script main.py from the terminal:

Bash

python main.py
Controls
Arrow Keys: Movement (Left/Right).

Space / Z / X: Action/Interact.

Q: Quit application.

Project Structure
The source code is organized as follows:

main.py: Entry point of the application; initializes the Pyxel app and the main game loop.

game.py: Contains the core Game class, managing the state machine and global game logic.

renderer.py: Handles all drawing operations, sprite rendering, and UI updates.

characters.py: Defines the Mario class and other character behaviors.

entities.py: Contains classes for game objects and interactive entities.

assets.pyxres: Binary resource file containing sprites, tilemaps, and sound effects.

Author: [Your Name / Student ID] Course: [Course Name] Date: December 2025
