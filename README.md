# 5000 Game Score Pad

A **Flask-based web app** to track scores for the dice game *5000* (or *Farkle*). This app provides an interactive score pad for players, automating the process of calculating totals, handling penalties for faults and zeros, and displaying a live scoreboard. 

The app was built in **1 day**, transitioning from a plain Python implementation to a basic Flask app with minimum Bootstrap-styled HTML.

## Features

- **Dynamic Player Setup**: Add players at the start of the game with unique color coding.
- **Real-Time Score Tracking**: Enter scores, faults, and zeros for players. The app keeps running totals and enforces game rules like penalties for faults/zeros.
- **Handle Curtom Total Removals**: Deals with a custom rule, whereby if one players running total matches that of a previous players, the latter running total is removed from the score board.
- **Final Round Logic**: Automatically detects when a player reaches 5000 points and initiates the final round.
- **Interactive Game Log**: Displays a running log of events during the game (e.g., faults, penalties, total removals).
- **Custom Styling with Bootstrap**: Uses a clean, responsive design for an intuitive user experience.

---

## Usage

https://5000.dpbcreative.com/

---

## How to Play

### Setup
- Enter player names on the setup screen.
- Leave the input blank and click **"Start Game"** when all players are added.

### Score Entry
- The app assumes you know the scoring and rules for the game
- Enter a score for the current player.
- Enter **F** for a fault or **0** for a zero.
- The app enforces penalties for 3 consecutive faults or zeros.

### Final Round
- When a player reaches **5000 points**, all players get one last turn.

### End Game
- After the final round, view the winner and final scores.

---

## Game Rules Handled

- **Faults:** After 3 faults, a player's turn is skipped.
- **Zeros:** After 3 zeros, the player's last score is deducted.
- **Duplicate Totals:** If a player's total matches another player's existing total, the duplicate is removed.
- **Winning:** The first player to reach or exceed 5000 triggers the final round.

---

## Technologies Used

- **Flask:** Backend framework for managing game logic.
- **Bootstrap:** Frontend styling for a responsive design.
- **HTML/Jinja2:** Templates for dynamic rendering.
- **Python:** Core game logic implementation.

---

## Future Improvements

- Add rules of play and scoring.
- Add support for customizable rules.
- Enhance UI with animations or sound effects.
- Implement a database for saving game progress.
- Convert to a mobile app using react.

---

## Credits

- **Developer:** Dominic Buzugbe
- **Dice Game Inspiration:** 5000/Farkle Rules

---

## Purpose

This repository is designed to demonstrate my skills in development.  
It is not intended for public use, redistribution, or commercial applications.

---

## License

This project is licensed under the **Non-Commercial Use License**.  
**You may view, use, and modify this code for personal or educational purposes only.**  
Commercial use, redistribution, or publication of this work in any form is strictly prohibited without explicit permission from the author.

If you're interested in using this project commercially, please contact me at dom@dpbcreative.com

