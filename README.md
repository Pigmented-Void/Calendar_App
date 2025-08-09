# Floating Calendar Widget

A floating, frameless, and transparent calendar app built with **Python** and **PyQt5**, featuring:

- Event storage in SQLite
- Event text and icons displayed directly in calendar date cells (Google Calendar-style)
- Colour coding for events
- Mini-mode toggle
- Click-and-drag positioning
- Optional "desktop widget" behaviour (sticks to desktop or always-on-bottom)
- Close button to exit the app

## PyQt5 Desktop App Features

- **Add, view, and delete events** by clicking calendar dates
- **Colour picker** for event background colour
- **Icon selector** for visual event categories
- **Display inline events** inside date cells
- **Transparent frameless design** with drag-to-move
- **Mini mode** hides extra controls for a smaller footprint
- **Events stored in SQLite database** (`calendar_events.db`)
- Windows-only option to position calendar above desktop background but below other windows

## Flask Web App Option

As an alternative, the calendar app can run as a **Flask-based web app** with:

- Same event storage in **SQLite**
- Add, view, and delete events through a browser UI
- Event notes, colours, and icons are shown alongside dates
- Simple web interface, or can be enhanced with JavaScript calendar libraries (e.g., FullCalendar)
- Runs in any modern browser; no installation required except running the Flask backend
- Supports hosting on cloud platforms or local server

### Flask Web App Features

- Add events via web form (date, note, colour, icon)
- View upcoming events in a list or calendar style
- Delete events from the browser
- Persistent event storage in SQLite
- Optional integration with JavaScript calendar libraries for richer UI
- Can be deployed on cloud hosts like Render, Heroku, or optionally converted to a static site with Flask-Frozen

## Requirements

- Python 3.9+
- **PyQt5** (for desktop app)
- **Flask** (for web app)
- SQLite (built into Python standard library)
- (Windows only) `ctypes` for desktop widget positioning (desktop app)
- For Flask web app deployment: optionally Flask-Frozen, GitHub Actions for CI/CD, and cloud hosting environment

## Installation & Running

### PyQt5 Desktop App

1. **Clone or download** the repository.
2. Install dependencies:
    ```
    pip install pyqt5
    ```
3. Run the app:
    ```
    python floating_calendar_widget.py
    ```
4. Use the interface to add/view/delete events directly inside the floating calendar window.

### Flask Web App

1. **Clone or download** the repository.
2. Install dependencies:
    ```
    pip install flask
    ```
3. Run the Flask server:
    ```
    python app.py
    ```
4. Open your browser and navigate to [http://localhost:5000](http://localhost:5000).

5. Add and manage events via the web interface.

## Deployment Notes

- **PyQt desktop app** runs locally on your machine and supports desktop widget features.
- **Flask app** can be deployed to cloud services like Render.com or Heroku for public access.
- You can convert Flask app to a static site (without dynamic backend) using Flask-Frozen and deploy to GitHub Pages.
- For automated testing and deployment, GitHub Actions workflows can run, test, and optionally deploy your Flask app.

## Usage (Both Versions)

- Select a date to add or view events.
- Enter an event note.
- Optionally pick a background colour and icon to categorize the event visually.
- Save the event (PyQt app uses native UI, Flask uses web form).
- Click events to edit or delete them.
- Toggle mini mode (desktop app) for a compact widget.
- Close the app as needed.

## Database

- Events are stored in a local SQLite database `calendar_events.db` located in the app directory.
- You can inspect the database file using SQLite tools or Python scripts.

## Screenshot

*(Insert screenshot of the desktop app or web app here)*

---

**License:** Free to use for personal projects.
