# Floating Calendar Widget

A floating, frameless, and transparent calendar app built with **Python** and **PyQt5**, featuring:
- Event storage in SQLite
- Event text and icons displayed directly in calendar date cells (Google Calendar-style)
- Colour coding for events
- Mini-mode toggle
- Click-and-drag positioning
- Optional "desktop widget" behaviour (sticks to desktop or always-on-bottom)
- Close button to exit the app

## Features
- **Add, view, and delete events** by clicking calendar dates
- **Colour picker** for event background colour
- **Icon selector** for visual event categories
- **Inline events display** inside date boxes
- **Transparent frameless design** with drag-to-move
- **Mini mode** hides extra controls for a smaller footprint
- **Stores events in SQLite database** (`calendar_events.db`)
- **Desktop behaviour**: can stay above desktop background but under other windows

## Requirements
- Python 3.9+
- PyQt5
- SQLite (built into Python standard library)
- (Windows only) `ctypes` for desktop widget positioning

## Installation
1. **Clone or download** the repository.
2. Install dependencies:
    ```
    pip install pyqt5
    ```
3. Run the app:
    ```
    python floating_calendar_widget.py
    ```

## Usage
- Click a date to select it.
- Enter event note and optionally:
  - Pick a colour
  - Select an icon
- Click **Add Event to Day** to save.
- Click an event in the list to edit or delete.
- Toggle **Mini Mode** for compact view.
- Press **Close** to exit.

## Notes
- Events are saved to `calendar_events.db` in the same directory as the script.
- On Windows, the calendar can be positioned to stay just above the desktop background but remain clickable.

## Screenshot
*(You can insert an image here if desired)*

---

**License:** Free to use for personal projects.
