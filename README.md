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

## Usage

https://test-5000-logic.onrender.com/
