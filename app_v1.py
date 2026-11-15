"""Version 1: a deliberately small, single-riddle prototype."""

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)


@app.get("/")
def index():
    return render_template("v1.html")


@app.post("/answer")
def answer():
    data = request.get_json(silent=True) or {}
    guess = data.get("answer", "")
    if not isinstance(guess, str) or not guess.strip():
        return jsonify(reply="Please enter an answer."), 400
    if guess.strip().casefold().strip(" .!?") == "piano":
        return jsonify(reply="Correct! You found the key and escaped the room.", escaped=True)
    return jsonify(reply="Not quite. Try again.", escaped=False)


if __name__ == "__main__":
    app.run(port=5001, debug=True)
