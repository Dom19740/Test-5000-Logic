def setup_game():
    players = []
    print("Welcome to the Farkle Score Pad!")
    print("Enter player names one by one. Press Enter on an empty line to finish.")

    while True:
        name = input("Enter player name (or press Enter to finish): ").strip()
        if not name:  # Finish if the user presses Enter
            if not players:
                print("You must enter at least one player!")
            else:
                break
        else:
            players.append(name)

    # Initialize score table with running totals for each player
    scores = {player: [0] for player in players}

    print("\nGame setup complete!")
    print("Players:", ", ".join(players))
    return players, scores

# Test the setup
players, scores = setup_game()
print("\nInitial Scores Table:")
for player, score in scores.items():
    print(f"{player}: {score}")
