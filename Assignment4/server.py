from flask import Flask, jsonify, request

app = Flask(__name__)

# Constants
SIZE = 7
COLS = "ABCDEFG"
MAX_TRIES = 3


# Game State
players = 0                 # how many players have joined
ships = {1: None, 2: None}  # player and their ship position
shots = {1: {}, 2: {}}      # shots[player] = attacks made by player, either hit or miss
turn = 1                    # whose turn it is
tries = MAX_TRIES
winner = None
last = None                 # most recent attack


def phase():
    
    # Game status
    if winner:
        return "finished"
    if players < 2 or None in ships.values():
        return "waiting"
    return "playing"


def valid_cell(text):
    text = str(text).strip().upper()
    if len(text) == 2 and text[0] in COLS and text[1] in "1234567":
        return text
    return None


def error(message, code=400):
    return jsonify({"error": message}), code


@app.route("/api/join", methods=["POST"])
def join():
    global players
    
    # Can only have two players
    if players >= 2:
        return error("Game is full.", 403)
    
    # Add player
    players += 1
    return jsonify({"player": players})


@app.route("/api/place", methods=["POST"])
def place():
    """
    Body: {"player": 1, "position": "B2"}
    """
    
    # Get JSON data from request
    data = request.get_json()
    
    # Get player number
    p = data.get("player")
    
    # Validate player
    if p not in (1, 2) or p > players:
        return error("Unknown player.")
    if ships[p] is not None:
        return error("Ship already placed.")
    
    # Validate ship position
    cell = valid_cell(data.get("position"))
    if cell is None:
        return error("Invalid position (use A1-G7).")
    ships[p] = cell
    return jsonify({"ok": True})


@app.route("/api/attack", methods=["POST"])
def attack():
    """
    Body: {"player": 1, "position": "D4"}
    """
    
    global turn, tries, winner, last
    data = request.get_json()
    p = data.get("player")
    
    # Validate player and game state
    if p not in (1, 2) or p > players:
        return error("Unknown player.")
    if phase() == "finished":
        return error("Game is over.")
    if phase() != "playing":
        return error("Game has not started yet.")
    if turn != p:
        return error("Not your turn.", 409)
    
    # Validate attack position
    cell = valid_cell(data.get("position"))
    if cell is None:
        return error("Invalid position (use A1-G7).")
    if cell in shots[p]:
        return error("You already attacked that position.")  # no try used

    # Get opponent
    opponent = 3 - p
    
    # Determine if hit or miss
    hit = (cell == ships[opponent])
    shots[p][cell] = "H" if hit else "X"
    tries -= 1
    
    # Record this attack
    last = {"by": p, "position": cell, "result": "HIT" if hit else "MISS"}

    # Determine if turn over or game won
    turn_over = False
    if hit:
        winner = p
    elif tries == 0:
        turn, tries, turn_over = opponent, MAX_TRIES, True

    return jsonify({"result": last["result"], "turn_over": turn_over, "winner": winner})


@app.route("/api/status", methods=["GET"])
def status():
    """
    Simple read-only request: ?player=1 -> boards, tries, turn, game status.
    """
    
    # Validate player
    p = request.args.get("player", type=int)
    if p not in (1, 2) or p > players:
        return error("Unknown player.")
    
    # Determine opponent, either 1 or 2
    opponent = 3 - p

    # Your grid
    your_grid = []
    for row in range(1, SIZE + 1):
        line = []
        for col in COLS:
            cell = col + str(row)
            line.append(shots[opponent].get(cell) or ("S" if cell == ships[p] else "?"))
        your_grid.append(line)

    # Show results of your attacks on opponent grid
    opponent_grid = [[shots[p].get(col + str(row), "?") for col in COLS]
                     for row in range(1, SIZE + 1)]

    # Return game state
    return jsonify({
        "phase": phase(),
        "turn": turn,
        "your_turn": phase() == "playing" and turn == p,
        "tries_remaining": tries,
        "max_tries": MAX_TRIES,
        "winner": winner,
        "last": last,
        "your_grid": your_grid,
        "opponent_grid": opponent_grid,
    })


if __name__ == "__main__":
    app.run(port=5000, threaded=False)