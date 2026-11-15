# AI Escape Room

A small Flask escape-room game demonstrating a progression from a one-riddle prototype (Version 1) to a validated, multi-puzzle game with optional AI-generated hints (Version 2).

## What it does

Players solve three riddles in sequence, request up to three hints, and can restart at any time. Puzzle answers and progress are checked by the server. An optional OpenAI-compatible Chat Completions API can phrase hints; it does not decide whether an answer is correct. If no API key is configured, the application clearly labels and uses built-in hints.

## Versions and development

### Version 1

Run `python app_v1.py` and open <http://127.0.0.1:5001>. This is the initial one-riddle prototype: one clue, one answer, and a basic correct/incorrect response.

### Version 2

Run `python app.py` and open <http://127.0.0.1:5000>. Version 2 introduces three sequential puzzles, server-side game state, input validation, bounded hints, restart, optional AI hint generation, and explicit handling for API failures. This addresses V1's limited gameplay and lack of recovery and state handling.

## Architecture

### Version 1

```text
Browser form
    │ answer (JSON)
    ▼
Flask /answer ── compares against one fixed answer
    │ result (JSON)
    └────────────────────────────► Browser feedback
```

### Version 2

```text
Browser UI
    │ game actions (JSON)
    ▼
Flask routes ──► Server-side game state and puzzle rules
    │                              │
    │ optional hint                └── answer validation and progression
    ▼
OpenAI-compatible Chat Completions API
    │ hint text (answers are not sent)
    └────────────────────────────► Browser UI
```

The in-memory game store is suitable for a local classroom demonstration. It is not durable across restarts and is not shared across multiple server workers. A production deployment should replace it with a persistent store such as Redis or a database, use a unique secret key, add rate limiting, and serve behind HTTPS.

## Requirements

- Python 3.10 or later
- Optional API key for AI-generated hints

## Install and run

From this directory, create and activate a virtual environment, then install dependencies:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` and set `FLASK_SECRET_KEY` to a long random value. To enable AI hints, set `AI_API_KEY`; configure `AI_BASE_URL` and `AI_MODEL` for your provider if needed. Never commit `.env` or put the API key in browser code.

Start Version 2:

```powershell
python app.py
```

Open <http://127.0.0.1:5000>. For the prototype, run `python app_v1.py` in a separate terminal and open <http://127.0.0.1:5001>.

## Tests

Run the automated checks with:

```powershell
pytest -q
```

| Case | Expected behavior |
|---|---|
| Correct answer with different capitalization and punctuation | Advances exactly one puzzle |
| Incorrect answer | Gives feedback and leaves progress unchanged |
| Empty or malformed message | Returns a clear validation error |
| More than 500 characters | Rejects the message without changing progress |
| Four hint requests | Allows three, rejects the fourth |
| API unavailable while AI hints are enabled | Returns an explicit error and does not consume a hint |
| Solve all puzzles, then restart | Marks completion, then clears progress and conversation |

Manual demonstration: start Version 2, submit a wrong answer, request a hint, solve all three riddles, and restart. Capture screenshots of the initial state, a hint/error interaction, and the escaped state for the portfolio repository.

## Limitations

- The game and session state live in process memory; restarting Flask clears active games.
- AI output is not guaranteed to be correct or to follow the no-answer instruction. The deterministic game rules remain authoritative.
- The included riddles and answers are demonstration content; change them to match the requirements agreed in class.
- The PDF brief was not readable in the coding environment, so confirm any class-specific requirements before submitting.

## GitHub portfolio checklist

Create a repository such as `AI-Escape-Room`, commit the two versions and supporting files in meaningful increments, add genuine screenshots or a short demo, and submit the repository URL. Review repository contents for secrets before publishing. Do not fabricate earlier commit history.
