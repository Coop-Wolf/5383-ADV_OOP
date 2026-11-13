"""
Battleship console client. Run one copy per player (each in its own terminal).

Requires:  pip install requests
"""
import random
import time
import requests

url = "http://localhost:5000/api"
COLS = "ABCDEFG"

# ask if going to play as human or computer
choice = input("Play as (1) Human or (2) Computer? ")
computer = (choice == "2")

# join the game
response = requests.post(url + "/join")

# check for error
if response.status_code != 200:
    print(response.json()["error"])
    raise SystemExit

# get player number
player = response.json()["player"]
print("You are Player", player)

# Allow user to place ship
while True:
    
    # Give computer a random position
    if computer:
        position = random.choice(COLS) + str(random.randint(1, 7))
        
    # Allow human to enter position
    else:
        position = input("Place your ship (e.g., B2): ")
        
    # Send request to place ship
    response = requests.post(url + "/place", json={"player": player, "position": position})
    
    # check for error, repeat until valid position is entered
    if response.status_code == 200:
        break
    print(response.json()["error"])


def show(s):
    """
    Print the status and both grids side by side.
    """
    
    # Print header and status
    print(f"\n========== BATTLESHIP - PLAYER {player} ==========")
    if s["phase"] == "finished":
        print("Status: Game Over")
    elif s["phase"] == "waiting":
        print("Status: Waiting for opponent...")
    elif s["your_turn"]:
        print("Status: Your Turn")
        print(f"Tries Remaining: {s['tries_remaining']}/{s['max_tries']}")
    else:
        print(f"Status: Waiting for Player {s['turn']}...")
    if s["last"] and s["last"]["by"] != player:
        print(f"Opponent attacked {s['last']['position']}: {s['last']['result']}")
        
    # Print both grids side by side
    header = "  " + " ".join(COLS)
    print(f"\n{'YOUR GRID':<18}  OPPONENT GRID")
    print(header + "    " + header)
    for i in range(7):
        print(f"{i + 1} {' '.join(s['your_grid'][i])}    {i + 1} {' '.join(s['opponent_grid'][i])}")
    print("S = Your Ship | ? = Unknown | X = Miss | H = Hit")


def computer_target(s):
    """
    Pick a random square that has not been attacked yet.
    """
    
    # Get opponent's grid and find unknown squares
    grid = s["opponent_grid"]
    unknown = [(r, c) for r in range(7) for c in range(7) if grid[r][c] == "?"]
    
    # Pick a random unknown square and return its position
    r, c = random.choice(unknown)
    time.sleep(0.5)
    return COLS[c] + str(r + 1)


# Game Loop
previous = None
while True:
    
    # Get the current game status
    s = requests.get(url + "/status", params={"player": player}).json()

    # If the status has changed, show it
    if s != previous:
        show(s)
        previous = s

    # Check if the game is over
    if s["phase"] == "finished":
        print("You win!" if s["winner"] == player else "You lose!")
        break

    # If its your turn, ask for a target and send an attack request
    if s["your_turn"]:
        
        # Computer picks random target
        if computer:
            target = computer_target(s)
        else:
            
            # Get target from user input
            target = input("Enter target position (e.g., D4): ")
            
        # Send attack request
        response = requests.post(url + "/attack", json={"player": player, "position": target})
        if response.status_code == 200:
            print("Result:", response.json()["result"] + "!")
        else:
            # Invalid attack
            print(response.json()["error"])
    else:
        # Wait for opponent's turn
        time.sleep(1)
