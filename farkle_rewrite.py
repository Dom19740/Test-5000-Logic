from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import random, json, logging

# Set up basic debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///farkle.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'my_secret_key'  # UPDATE FOR DEVELOPMENT, USE .ENV

db = SQLAlchemy(app)

# Models
class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_started = db.Column(db.Boolean, default=False)
    final_round_started = db.Column(db.Boolean, default=False)
    final_round_turns = db.Column(db.Integer, default=0)
    messages = db.Column(db.Text, default='[]')

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    color = db.Column(db.String(7), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    scores = db.Column(db.Text, default='[]')
    faults = db.Column(db.Integer, default=0)
    zeros = db.Column(db.Integer, default=0)

db.create_all()

color_options = [
    '#ff0088', '#ffa07a', '#ffd500', '#34c760', '#00c3ff', '#6c5ce7', '#9824aa', '#000',
]

# Function to load previous winners from file
def load_previous_winners():
    try:
        with open('previous_winners.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []

# Function to save previous winners to file
def save_winner(winner, winner_score):
    logger.debug(f"1. SAVING WINNER: {winner} WITH SCORE: {winner_score}")  # Debugging winner saving
    previous_winners = load_previous_winners()
    previous_winners.insert(0, {'name': winner, 'score': winner_score})
    with open('previous_winners.json', 'w') as f:
        json.dump(previous_winners, f)

@app.route('/')
def index():
    game = Game.query.filter_by(game_started=False).first()
    if not game:
        game = Game()
        db.session.add(game)
        db.session.commit()
    previous_winners = load_previous_winners()
    return render_template('setup_game.html', previous_winners=previous_winners, game_id=game.id)

@app.route('/setup', methods=['POST'])
def setup():
    game_id = request.form.get('game_id')
    game = Game.query.get(game_id)
    player_name = request.form.get('player_name').strip()

    if player_name:
        color = random.choice(color_options)
        color_options.remove(color)
        player = Player(name=player_name, color=color, game_id=game.id)
        db.session.add(player)
        db.session.commit()
        players = Player.query.filter_by(game_id=game.id).all()
        return render_template('setup_game.html', players=players, game_id=game.id)
    elif Player.query.filter_by(game_id=game.id).count() > 0:
        game.game_started = True
        db.session.commit()
        return redirect(url_for('game', game_id=game.id))
    else:
        return render_template('setup_game.html', error="Please enter at least one player.", game_id=game.id)

@app.route('/game/<int:game_id>', methods=['GET', 'POST'])
def game(game_id):
    game = Game.query.get(game_id)
    players = Player.query.filter_by(game_id=game.id).all()
    player_index = session.get('player_index', 0)
    current_player = players[player_index]

    if request.method == 'POST':
        player = Player.query.get(request.form['player_id'])
        score_input = request.form.get('score').strip().upper()
        message = f"{player.name} scored {score_input}."
        messages = json.loads(game.messages)
        messages.append(message)
        game.messages = json.dumps(messages)

        if score_input == "F":
            player.faults += 1
            if player.faults == 3:
                message = f"🚫  Fault Warning: {player.name} has 3 faults! Moving to next player."
                messages.append(message)
                player.faults = 0
                db.session.commit()
                return handle_next_turn(game, players)
            db.session.commit()
            return redirect(url_for('game', game_id=game.id))
        elif score_input == "0" or score_input == "":
            player.zeros += 1
            if player.zeros == 3:
                message = f"⚠️  Zero Penalty: {player.name} loses their last score."
                messages.append(message)
                scores = json.loads(player.scores)
                if scores:
                    scores.pop()
                player.scores = json.dumps(scores)
                player.zeros = 0
                db.session.commit()
                return handle_next_turn(game, players)
        else:
            try:
                score = int(score_input)
                scores = json.loads(player.scores)
                current_total = scores[-1] if scores else 0
                new_total = current_total + score
                scores.append(new_total)
                player.scores = json.dumps(scores)
                player.zeros = 0
                for other_player in players:
                    if other_player.id != player.id:
                        other_scores = json.loads(other_player.scores)
                        if new_total in other_scores:
                            other_scores.remove(new_total)
                            other_player.scores = json.dumps(other_scores)
                            message = f"⚠️  {new_total} is already a total for {other_player.name}, removing their score!"
                            messages.append(message)
                            break
                if new_total >= 5000 and not game.final_round_started:
                    game.final_round_started = True
                    message = f"🎉 {player.name} has reached a score of {new_total}! Final round begins: Every player gets one more turn."
                    messages.append(message)
                game.messages = json.dumps(messages)
                db.session.commit()
            except ValueError:
                pass
        return handle_next_turn(game, players)

    table = generate_table(players)
    messages = json.loads(game.messages)
    return render_template('game.html', messages=messages, players=players, table=table, current_player=current_player)

def handle_next_turn(game, players):
    player_index = session.get('player_index', 0)
    player_index = (player_index + 1) % len(players)
    session['player_index'] = player_index

    if game.final_round_started:
        game.final_round_turns += 1
        if game.final_round_turns >= len(players):
            return redirect(url_for('end_game', game_id=game.id))
    db.session.commit()
    return redirect(url_for('game', game_id=game.id))

@app.route('/end_game/<int:game_id>', methods=['GET'])
def end_game(game_id):
    game = Game.query.get(game_id)
    players = Player.query.filter_by(game_id=game.id).all()
    winner = max(players, key=lambda player: json.loads(player.scores)[-1] if json.loads(player.scores) else 0)
    winner_score = json.loads(winner.scores)[-1] if json.loads(winner.scores) else 0
    save_winner(winner.name, winner_score)
    table = generate_table(players)
    messages = json.loads(game.messages)
    return render_template('end_game.html', winner=winner.name, winner_score=winner_score, table=table, messages=messages)

@app.route('/reset', methods=['POST'])
def reset():
    db.drop_all()
    db.create_all()
    return redirect(url_for('index'))

def generate_table(players):
    max_rounds = max(len(json.loads(player.scores)) for player in players) if players else 0
    table_html = '<table class="table table-bordered table-hover text-center">'
    table_html += '<thead class="table-dark">'
    table_html += '<tr><th>Name</th>'
    for player in players:
        table_html += f'<th style="background-color: {player.color}">{player.name}</th>'
    table_html += '</tr></thead>'
    table_html += '<tr><th>Total</th>'
    for player in players:
        scores = json.loads(player.scores)
        current_total = scores[-1] if scores else 0
        table_html += f'<td>{current_total}</td>'
    table_html += '</tr>'
    table_html += '<tr><th>Faults</th>'
    for player in players:
        table_html += f'<td>{player.faults}</td>'
    table_html += '</tr>'
    table_html += '<tr><th>Zeroes</th>'
    for player in players:
        table_html += f'<td>{player.zeros}</td>'
    table_html += '</tr>'
    table_html += '<tr><td colspan="100%" class="table-secondary"></td></tr>'
    table_html += '<tbody>'
    for round_index in range(max_rounds):
        table_html += f'<tr><th>Score {round_index + 1}</th>'
        for player in players:
            scores = json.loads(player.scores)
            score_for_round = scores[round_index] if round_index < len(scores) else ""
            table_html += f'<td>{score_for_round}</td>'
        table_html += '</tr>'
    table_html += '</tbody></table>'
    return table_html

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0')