# Copyright (c) 2024 dpb creative
# This code is licensed for non-commercial use only. See LICENSE file for details.

from flask import Flask, render_template, request, redirect, url_for, session
from tabulate import tabulate
import os, random, json, logging

# Set up basic debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Enable debug mode in development
app.debug = True
app.secret_key = 'my_secret_key' # UPDATE FOR DEVELOPMENT, USE .ENV

# Global variables
previous_winners_file = 'previous_winners.json'
color_options = [
    '#cf2a33',
    '#ffa07a',
    '#ffd500',
    '#34c760',
    '#00c3ff',
    '#6c5ce7',
    '#9824aa',
    '#cf33ab',
]

# Function to load previous winners from file
def load_previous_winners():
    try:
        with open(previous_winners_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []

# Function to save previous winners to file
def save_winner(winner, winner_score):
    #logger.debug(f"1. SAVING WINNER: {winner} WITH SCORE: {winner_score}")  # Debugging winner saving
    previous_winners = load_previous_winners()
    previous_winners.insert(0, {'name': winner, 'score': winner_score})
    with open(previous_winners_file, 'w') as f:
        json.dump(previous_winners, f)

@app.route('/')
def index():
    if not session.get('game_started', False):
        previous_winners = load_previous_winners()
        return render_template('setup_game.html', previous_winners=previous_winners)
    
    #logger.debug(f"2. INDEX ROUTE: REDIRECTING to 'game'. Player turn: {session.get('player_index', 0)}")  # Debugging redirection
    return redirect(url_for('game'))

@app.route('/setup', methods=['POST'])
def setup():
    #logger.debug(f"3. SETUP ROUTE STARTED")  # Debugging statement
    global color_options
    player_name = request.form.get('player_name').strip()

    # Initialize session variables if not already set
    if 'players' not in session:
        session['players'] = []
        session['scores'] = {}
        session['faults'] = {}
        session['zeros'] = {}
        session['player_colors'] = {}
        session['player_index'] = 0
        session['game_started'] = False
        session['final_round_started'] = False
        session['final_round_turns'] = 0
        session['messages'] = []
        #logger.debug(f"3. COLOR OPTIONS {color_options}")  # Debugging statement
        session['color_options'] = color_options.copy()

    players = session['players']
    scores = session['scores']
    faults = session['faults']
    zeros = session['zeros']
    player_colors = session['player_colors']
    player_index = session['player_index']
    game_started = session['game_started']
    final_round_started = session['final_round_started']
    final_round_turns = session['final_round_turns']
    messages = session['messages']
    color_options = session['color_options']

    if player_name:  # If player name is provided
        players.append(player_name)
        session['players'] = players  # Save updated list back to session
        
        #logger.debug(f"4. PLAYER ADDED: {player_name}")
        #logger.debug(f"5. PLAYERS: {players}")

        return render_template('setup_game.html', players=players)  # Refresh page with updated player list

    elif len(players) > 0:  # Start the game if no name is entered and there are players
        scores = {player: [] for player in players}
        faults = {player: 0 for player in players}
        zeros = {player: 0 for player in players}
        player_colors = {}  # Initialize player_colors dictionary
        
        #logger.debug(f"6.SCORES: {scores}")  # Debugging statement
        #logger.debug(f"7.FAULTS: {faults}")  # Debugging statement
        #logger.debug(f"8.ZEROS: {zeros}")  # Debugging statement

        player_index = 0 

        for player in players:
            color = random.choice(color_options)
            player_colors[player] = color
            color_options.remove(color)  # Remove the assigned color

        #logger.debug(f"9.PLAYER COLORS: {player_colors}")  # Debugging statement

        game_started = True

        # Save updated session variables
        session['scores'] = scores
        session['faults'] = faults
        session['zeros'] = zeros
        session['player_colors'] = player_colors
        session['player_index'] = player_index
        session['game_started'] = game_started
        session['color_options'] = color_options

        return redirect(url_for('game'))
    else:
        # If no player names have been entered, show an error
        return render_template('setup_game.html', error="Please enter at least one player.")

@app.route('/game', methods=['GET', 'POST'])
def game():
    # Retrieve data from session
    players = session.get('players', [])
    scores = session.get('scores', {})
    faults = session.get('faults', {})
    zeros = session.get('zeros', {})
    player_colors = session.get('player_colors', {})
    player_index = session.get('player_index', 0)
    game_started = session.get('game_started', False)
    final_round_started = session.get('final_round_started', False)
    final_round_turns = session.get('final_round_turns', 0)
    messages = session.get('messages', [])

    #logger.debug(f"10.GAME ROUTE STARTED")  # Debugging statement
    #logger.debug(f"11.PLAYERS: {players}")  # Debugging statement
    #logger.debug(f"12.SCORES: {scores}")  # Debugging statement
    #logger.debug(f"13.FAULTS: {faults}")  # Debugging statement
    #logger.debug(f"14.ZEROS: {zeros}")  # Debugging statement
    #logger.debug(f"15.PLAYER COLORS: {player_colors}")  # Debugging statement

    # Initialize an empty message
    message = ''

    if request.method == 'POST':
        player = players[player_index]
        score_input = request.form.get('score').strip().upper()

        #logger.debug(f"16.Player: {player}, Score Input: {score_input}")  # Debugging statement

        message = f"{player} scored {score_input}."
        messages.append(message)

        if score_input == "F":
            faults[player] += 1

            if faults[player] == 3:
                message = f"{player} 🚫  3 faults - Moving to next player."
                messages.append(message)

                faults[player] = 0  # Reset after 3 faults
                return handle_next_turn()
            
            session['faults'] = faults  # Save updated faults back to session
            session['messages'] = messages  # Save updated messages back to session
            #logger.debug(f"Updated ZEROS: {zeros}")  # Debugging statement
            #logger.debug(f"17.Redirecting to 'game'. Player turn: {player_index}")  # Debugging redirection
            return redirect(url_for('game'))

        # Handle "0" for zero points
        elif score_input == "0" or score_input is None or score_input.strip() == "":
            zeros[player] += 1
            if zeros[player] == 3:
                message = f"{player} ⚠️  Zero Penalty - Lose last score."
                messages.append(message)

                if scores[player]:
                    scores[player].pop()  # Remove last score if 3 zeros
                zeros[player] = 0
                return handle_next_turn()
            session['zeros'] = zeros  # Save updated zeros back to session
            session['messages'] = messages  # Save updated messages back to session

        # Handle regular score input
        else:
            try:
                score = int(score_input)

                #logger.debug(f"18.player: {player}, scores: {scores}") # Debug

                current_total = scores[player][-1] if scores[player] else 0
                new_total = current_total + score
                scores[player].append(new_total)
                zeros[player] = 0  # Reset zero counter on a valid score

                #logger.debug(f"player: {player}, scores after update: {scores}") # Debug

                # Check if the new total exists in any other player's running totals
                for other_player in players:
                    if other_player != player:
                        if new_total in scores[other_player]:
                            scores[other_player].remove(new_total)  # Remove the exact match
                            message = f"{other_player} ⚠️  has score {new_total}, removing their score!"
                            messages.append(message)
                            break  # Exit the loop once the total is found and reverted

                # Check if the player has reached or exceeded 5000 points
                if new_total >= 5000 and not final_round_started:
                    final_round_started = True
                    message = f"{player} has reached a score of {new_total} 🎉! Final round begins: Every player gets one more turn."
                    messages.append(message)

                # Save updated to session
                session['scores'] = scores
                session['final_round_started'] = final_round_started

            except ValueError:
                pass

        # Move to the next player
        return handle_next_turn()

    # Generate the score table as a string
    table = generate_table(players, scores, faults, zeros)

    # Get the current player's name to display it in the form
    logger.debug(f"player_index: {player_index}, players: {players}")

    current_player = players[player_index]

    return render_template('game.html',
                           message=message,
                           messages=messages,
                           players=players,
                           scores=scores,
                           faults=faults, 
                           zeros=zeros,
                           table=table,
                           current_player=current_player,
                           player_colors=player_colors,
                           )

def handle_next_turn():
    """
    Handles advancing to the next player's turn, including logic for the final round.
    """
    players = session.get('players', [])
    player_index = session.get('player_index', 0)
    final_round_started = session.get('final_round_started', False)
    final_round_turns = session.get('final_round_turns', 0)

    # Debugging statement to check the state of players list
    #logger.debug(f"19b.handle_next_turn: players list: {players}")

    if not players:
        #logger.error("19c.handle_next_turn: players list is empty!")
        return redirect(url_for('setup'))

    # Move to the next player
    #logger.debug(f"20. Moving to next turn. Current player index: {player_index}")  # Debugging player turn
    player_index = (player_index + 1) % len(players)
    session['player_index'] = player_index

    if final_round_started:
        final_round_turns += 1
        session['final_round_turns'] = final_round_turns

        # End the game after every player has had their final turn
        if final_round_turns >= len(players):
            return redirect(url_for('end_game'))

    #logger.debug(f"21. Redirecting to 'game'. Player turn: {player_index}")  # Debugging redirection
    return redirect(url_for('game'))

@app.route('/end_game', methods=['GET'])
def end_game():
    # Retrieve data from session
    players = session.get('players', [])
    scores = session.get('scores', {})
    faults = session.get('faults', {})
    zeros = session.get('zeros', {})
    messages = session.get('messages', [])

    # Calculate and pass necessary data to the end game template
    winner = max(scores, key=lambda player: scores[player][-1] if scores[player] else 0)
    winner_score = scores[winner][-1] if scores[winner] else 0

    # Save the winner to the previous winners file
    save_winner(winner, winner_score)

    table = generate_table(players, scores, faults, zeros)

    return render_template('end_game.html', winner=winner, winner_score=winner_score, table=table, messages=messages)

@app.route('/reset', methods=['POST'])
def reset():
    # Clear session variables
    session.clear()
    return redirect(url_for('index'))

def generate_table(players, scores, faults, zeros):
    # Retrieve scores, faults, and zeros from session
    players = session.get('players', [])
    scores = session.get('scores', {})
    faults = session.get('faults', {})
    zeros = session.get('zeros', {})
    player_colors = session.get('player_colors', {})

    # Find the maximum number of rounds (by the longest score list of any player)
    max_rounds = max(len(score) for score in scores.values()) if scores else 0

    # Build the table header
    table_html = '<table class="table table-bordered table-hover text-center">'
    table_html += '<thead class="table-dark">'
    table_html += '<tr><th>Name</th>'
    for player in players:
        logger.debug(f"22. player: {player}, player_colors: {player_colors}") # Debug table

        table_html += f'<th style="background-color: {player_colors[player]}">{player}</th>'
    table_html += '</tr></thead>'

    # Add row for current total
    table_html += '<tr><th>Total</th>'
    for player in players:
        current_total = scores[player][-1] if scores[player] else 0
        table_html += f'<td>{current_total}</td>'
    table_html += '</tr>'

    # Add row for faults
    table_html += '<tr><th>Faults</th>'
    for player in players:
        fault_count = faults.get(player, 0)
        if fault_count == 1:
            table_html += f'<td style="background-color: yellow">{fault_count}</td>'
        elif fault_count == 2:
            table_html += f'<td style="background-color: orange">{fault_count}</td>'
        else:
            table_html += f'<td>{fault_count}</td>'
    table_html += '</tr>'

    # Add row for zeros
    table_html += '<tr><th>Zeroes</th>'
    for player in players:
        zero_count = zeros.get(player, 0)
        if zero_count == 1:
            table_html += f'<td style="background-color: yellow">{zero_count}</td>'
        elif zero_count == 2:
            table_html += f'<td style="background-color: orange">{zero_count}</td>'
        else:
            table_html += f'<td>{zero_count}</td>'
    table_html += '</tr>'

    # Add a blank row for spacing between scores and faults/zeros
    table_html += '<tr><td colspan="100%" class="table-secondary"></td></tr>'

    # Add rows for each round
    table_html += '<tbody>'
    for round_index in range(max_rounds):
        table_html += f'<tr><th>Score {round_index + 1}</th>'
        for player in players:
            score_for_round = scores[player][round_index] if round_index < len(scores[player]) else ""
            table_html += f'<td>{score_for_round}</td>'
        table_html += '</tr>'

    # Close the table
    table_html += '</tbody></table>'
    return table_html

if __name__ == "__main__":
    app.run(host='0.0.0.0')