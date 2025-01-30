from tabulate import tabulate


def setup_game():
    players = []
    print("Welcome to the 5000 Score Pad!")
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

    # Initialize score table with empty lists for each player (no starting score)
    scores = {player: [] for player in players}

    print("\nGame setup complete!")
    print("Players:", ", ".join(players))

    return players, scores


def display_table(players, scores, faults, zeros):
    # Prepare the table with player names as header
    table = [["Name"] + players]  # First row with player names
    max_rounds = max(len(score) for score in scores.values())  # Get max number of rounds

    # If the first score exists, display it as "Total 1"
    if max_rounds > 0:
        row = [f"Total 1"]
        for player in players:
            # Append the player's score for the first round (or a space if not available)
            row.append(scores[player][0] if len(scores[player]) > 0 else " ")
        table.append(row)

    # Start from Total 2 (i = 1) if there are more rounds
    for i in range(1, max_rounds):  # Start from Total 2 (i = 1)
        row = [f"Total {i + 1}"]
        for player in players:
            # Append the player's score for the current round (or a space if not available)
            row.append(scores[player][i] if i < len(scores[player]) else " ")
        table.append(row)

    # Add a blank row for spacing between totals and faults
    table.append([])  # Empty row for spacing

    # Add row for faults
    row = ["Faults"] + [str(faults[player]) for player in players]
    table.append(row)

    # Add row for zeroes
    row = ["Zeroes"] + [str(zeros[player]) for player in players]
    table.append(row)

    # Print the table
    print("\nCurrent Scores:")
    print(tabulate(table, tablefmt="grid"))


def play_game(players, scores, faults, zeros):
    player_index = 0  # Start with the first player
    while True:
        # Select current player
        player = players[player_index]
        print(f"\n{player}'s turn!")

        # Input score
        score_input = input(f"Enter score for {player} (or 'F' for fault, '0' for zero points): ").strip().upper()

        # Handle fault or zero input
        if score_input == "F":
            faults[player] += 1
            if faults[player] == 3:
                print(f"\n⚠️  Fault Warning: {player} has 3 faults! Moving to next player.")
                faults[player] = 0  # Reset fault count after reaching 3
                player_index = (player_index + 1) % len(players)  # Move to next player
                input("Press Enter to continue...")  # Pause for player to read message
                continue  # Skip to the next loop iteration (next player's turn)
            else:
                print(f"Fault recorded for {player}. Total faults: {faults[player]}.")
                
        elif score_input == "0":
            zeros[player] += 1
            if zeros[player] == 3:
                print(f"\n⚠️  Zero Penalty: {player} loses their last score!")
                # If there are any scores, remove the last one (even if it's Total 1)
                if scores[player]:
                    scores[player].pop()
                zeros[player] = 0
                input("Press Enter to continue...")  # Only break after the 3rd zero
            else:
                print(f"Zero points recorded for {player}. Total zeros: {zeros[player]}.")
        else:
            try:
                score = int(score_input)
                current_total = scores[player][-1] if scores[player] else 0  # Handle if no score yet
                new_total = current_total + score
                scores[player].append(new_total)
                zeros[player] = 0  # Reset zero counter on a valid score
                print(f"Score added! {player}'s new total: {new_total}")

                # Check if the new total exists in any other player's running totals
                for other_player in players:
                    if other_player != player:
                        if new_total in scores[other_player]:
                            # If the total matches, remove the exact match from the other player's stack
                            print(f"\n⚠️  {new_total} is already a total for {other_player}, removing {other_player}'s score!")
                            scores[other_player].remove(new_total)  # Remove the exact match
                            break  # Exit the loop once the total is found and reverted

            except ValueError:
                print("Invalid input. Please enter a number, 'F', or '0'.")

        # Display the updated table after every player's turn
        display_table(players, scores, faults, zeros)

        # Move to next player only if no fault or after 3 faults
        if score_input != "F" or faults[player] == 0:  # Skip advancing the player on faults
            player_index = (player_index + 1) % len(players)


# Set up the game and start playing
players, scores = setup_game()
print('\n')
faults = {player: 0 for player in players}
zeros = {player: 0 for player in players}
play_game(players, scores, faults, zeros)
