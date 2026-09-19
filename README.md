# Tents Puzzle (Python / Pygame)

A Python implementation of the classic **Tents and Trees** logic puzzle, built as a university project. Each level presents a grid with trees and row/column target counts; the goal is to place a tent next to each tree so that the counts match and no two tents touch, even diagonally.

## Overview

Beyond just an interactive puzzle board, the project includes a **backtracking solver** that computes a valid solution for every level as soon as it loads. This solution powers an interactive hint system (with a blinking highlight on the next correct cell) as well as "reveal solution" shortcuts, and is also used to automatically detect when a level has been solved correctly.

## Key Features

- **Core puzzle mechanics:** click to cycle a cell between empty, grass, and tent; row/column target counts shown as headers
- **Automatic solver:** a backtracking algorithm finds a valid tent placement for each level, respecting row/column counts and the no-adjacent-tents rule
- **Interactive hints:** highlights the next correct cell with a timed blinking animation, based on the solver's output
- **Level progression:** multiple puzzles of increasing size and difficulty (8x8, 12x12, 16x16, 20x20), loaded from plain text files and automatically sorted by size and difficulty
- **Validation & feedback:** detects invalid placements (touching tents) and confirms when a level is fully and correctly solved
- **Keyboard shortcuts:** next level, reset, reveal grass/tents solution, and trigger a hint

## Tech Stack

- **Language:** Python 3
- **Graphics/Input:** Pygame (via the provided `g2d` wrapper)
- **Algorithm:** custom recursive backtracking solver

Built on top of a minimal board-game framework (`g2d.py`, `boardgame.py`, `boardgamegui.py`) provided as course material, extended with a custom GUI subclass to support the blinking hint animation.

## Project Structure

```
Tents puzzle/
├── g2d.py                          # 2D rendering/input wrapper around Pygame (course-provided)
├── boardgame.py                    # Generic BoardGame interface (course-provided)
├── boardgamegui.py                 # Generic grid-based GUI for board games (course-provided)
├── game.py                         # Tents game logic, solver, hint system, and custom GUI
└── tents-*.txt                     # Puzzle level files (grid size, difficulty, tree layout)
```

## Running the Game

**1. Requirements**
- Python 3.10+
- Pygame (installed automatically on first run if missing, or manually with `pip install pygame`)

**2. Start the game**
```
python game.py
```

**3. Controls**
- **Left click:** cycle a cell between empty → grass → tent
- **N:** next level
- **R:** reset current level
- **G:** reveal the grass placement of the solution
- **T:** reveal the tent placement of the solution
- **A:** show a hint (blinking cell)

---

> Built on top of a minimal board-game framework (`g2d.py`, `boardgame.py`, `boardgamegui.py`) provided as course material.
