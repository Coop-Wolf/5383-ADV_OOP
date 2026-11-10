from flask import Flask, request, jsonify

server = Flask(__name__)

MAX_TRIES = 5

secret = None
num_tries = 0
game_over = False


def parse_number(data):
    """Return an int from 1-100, or None if invalid."""
    if not data:
        return None
    n = data.get("number")
    if isinstance(n, bool) or not isinstance(n, int) or not 1 <= n <= 100:
        return None
    return n


@server.route('/api/get_state', methods=['GET'])
def get_state():
    return jsonify({
        "number_set": secret is not None,
        "tries_used": num_tries,
        "tries_left": MAX_TRIES - num_tries,
        "game_over": game_over,
    })


@server.route('/api/set_number', methods=['POST'])
def set_number():
    global secret, num_tries, game_over
    n = parse_number(request.get_json(silent=True))
    if n is None:
        return jsonify({"error": "number must be an integer from 1 to 100"}), 400

    secret = n
    num_tries = 0
    game_over = False
    return jsonify({"result": "success"})


@server.route('/api/guess_number', methods=['POST'])
def guess_number():
    global num_tries, game_over

    if secret is None:
        return jsonify({"error": "The boss hasn't set a number yet"}), 409
    if game_over:
        return jsonify({"error": "Game is over. Wait for a new number."}), 403

    num = parse_number(request.get_json(silent=True))
    if num is None:
        return jsonify({"error": "guess must be an integer from 1 to 100"}), 400
    
    
    
    

    num_tries += 1

    if num == secret:
        game_over = True
        return jsonify({"result": "correct", "tries_used": num_tries, "game_over": True})

    hint = "too low" if num < secret else "too high"

    if num_tries >= MAX_TRIES:
        game_over = True
        return jsonify({"result": hint, "tries_left": 0, "game_over": True,
                        "message": f"Out of guesses! The answer was {secret}."})

    return jsonify({"result": hint, "tries_left": MAX_TRIES - num_tries, "game_over": False})


if __name__ == "__main__":
    server.run(port=5000, threaded=False)