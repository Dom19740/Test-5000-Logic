from flask import Flask, render_template, request, redirect, url_for, flash
from tabulate import tabulate
import os


app = Flask(__name__)
app.secret_key = 'my_secret_key'

# Global variables
players = []
scores = {}
faults = {}
zeros = {}
player_index = 0
game_started = False

@app.route('/')
def index():
    if not game_started:
        return render_template('setup_game.html')
    return redirect(url_for('game'))

@app.route('/setup', methods=['POST'])
def setup():
    global players, scores, faults, zeros, game_started, player_index

    player_name = request.form.get('player_name').strip()

    if player_name:  # Add the player if a name is entered
        players.append(player_name)
        return render_template('setup_game.html', players=players)  # Continue adding players
    elif len(players) > 0:  # Start the game if no name is entered and there are players
        scores = {player: [] for player in players}
        faults = {player: 0 for player in players}
        zeros = {player: 0 for player in players}
        player_index = 0  # Initialize player_index to 0 (first player)
        game_started = True
        return redirect(url_for('game'))
    else:
        # If no player names have been entered, show an error
        return render_template('setup_game.html', error="Please enter at least one player.")



@app.route('/game', methods=['GET', 'POST'])
def game():
    global players, scores, faults, zeros, player_index

    # Initialize an empty message
    message = ''

    if request.method == 'POST':
        player = request.form['player']
        score_input = request.form['score'].strip().upper()

        # Handle "F" for fault
        if score_input == "F":
            faults[player] += 1

            if faults[player] == 3:
                # Add a message for fault warning
                message = (f"\n⚠️  Fault Warning: {player} has 3 faults! Moving to next player.")
                flash(message)

                faults[player] = 0  # Reset after 3 faults
                return redirect(url_for('next_turn'))

        # Handle "0" for zero points
        elif score_input == "0":
            zeros[player] += 1
            if zeros[player] == 3:
                message = (f"\n⚠️  Zero Penalty: {player} loses their last score.")
                flash(message)

                if scores[player]:
                    removed_score = scores[player].pop()  # Remove last score if 3 zeros
                zeros[player] = 0
                return redirect(url_for('next_turn'))

        # Handle regular score input
        else:
            try:
                score = int(score_input)
                current_total = scores[player][-1] if scores[player] else 0
                new_total = current_total + score
                scores[player].append(new_total)
                zeros[player] = 0  # Reset zero counter on a valid score

                # Check if the new total exists in any other player's running totals
                for other_player in players:
                    if other_player != player:
                        if new_total in scores[other_player]:
                            scores[other_player].remove(new_total)  # Remove the exact match
                            #message.append(f"⚠️ {new_total} is already a total for {other_player}, removing their score!")
                            message = (f"\n⚠️  {new_total} is already a total for {other_player}, removing their score!")
                            flash(message)
                            
                            break  # Exit the loop once the total is found and reverted

            except ValueError:
                pass

        # After processing the score, move to the next player
        return redirect(url_for('next_turn'))

    # Generate the score table as a string using tabulate
    table = generate_table(players, scores, faults, zeros)

    # Get the current player's name to display it in the form
    current_player = players[player_index]
    
    print("base message:", message)
    return render_template('game.html', message=message, players=players, scores=scores, faults=faults, zeros=zeros, table=table, current_player=current_player)






@app.route('/next_turn')
def next_turn():
    global player_index

    # Move to the next player
    player_index = (player_index + 1) % len(players)
    
    # Redirect back to the game page for the next player's turn
    return redirect(url_for('game'))

@app.route('/reset', methods=['POST'])
def reset():
    global players, scores, faults, zeros, game_started
    players = []
    scores = {}
    faults = {}
    zeros = {}
    game_started = False
    return redirect(url_for('index'))

def generate_table(players, scores, faults, zeros):
    # Find the maximum number of rounds (by the longest score list of any player)
    max_rounds = max(len(score) for score in scores.values()) if scores else 0

    # Start building the table
    table = [["Name"] + players]  # Header row with player names

    # Generate rows for each round
    for round_index in range(max_rounds):
        row = [f"Total {round_index + 1}"]  # Row for this round
        for player in players:
            score_for_round = scores[player][round_index] if round_index < len(scores[player]) else " "
            row.append(score_for_round)
        table.append(row)

    # Add a blank row for spacing between scores and faults/zeros
    table.append([])

    # Add row for faults
    row = ["Faults"] + [str(faults.get(player, 0)) for player in players]
    table.append(row)

    # Add row for zeros
    row = ["Zeroes"] + [str(zeros.get(player, 0)) for player in players]
    table.append(row)

    # Return the table as a string using the tabulate library
    return tabulate(table, tablefmt="grid")

if __name__ == '__main__':
    app.run(debug=True)
