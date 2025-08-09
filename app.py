from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import date

app = Flask(__name__)

DB_NAME = "calendar_events.db"

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# Ensure table exists
with get_db() as conn:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            note TEXT,
            colour TEXT,
            icon TEXT
        )
    """)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        event_date = request.form["date"]
        note = request.form["note"]
        colour = request.form["colour"]
        icon = request.form["icon"]
        with get_db() as conn:
            conn.execute(
                "INSERT INTO events (date, note, colour, icon) VALUES (?, ?, ?, ?)",
                (event_date, note, colour, icon)
            )
        return redirect(url_for("index"))

    with get_db() as conn:
        events = conn.execute("SELECT * FROM events ORDER BY date").fetchall()

    return render_template("index.html", events=events, today=date.today())

@app.route("/delete/<int:event_id>")
def delete(event_id):
    with get_db() as conn:
        conn.execute("DELETE FROM events WHERE id=?", (event_id,))
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
