import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QCalendarWidget, QTextEdit, QPushButton,
    QMessageBox, QColorDialog, QHBoxLayout, QLabel, QComboBox, QListWidget, QListWidgetItem
)
from PyQt5.QtGui import QTextCharFormat, QBrush, QColor, QFont
from PyQt5.QtCore import Qt, QPoint, QDate

# ---- Custom Calendar Class to Draw Events in Cells ----
class EventCalendarWidget(QCalendarWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.events_by_date = {}

    def set_events(self, events_dict):
        self.events_by_date = events_dict
        self.update()

    def paintCell(self, painter, rect, date):
        super().paintCell(painter, rect, date)
        if date in self.events_by_date:
            painter.save()
            font = painter.font()
            font.setPointSize(7)
            painter.setFont(font)
            y_offset = rect.top() + 15
            for icon, note, colour in self.events_by_date[date][:3]:
                painter.setPen(QColor(colour) if colour else Qt.white)
                text = f"{icon} {note}" if icon else note
                painter.drawText(rect.left() + 2, y_offset, rect.width() - 4, 10,
                                 Qt.TextSingleLine | Qt.AlignLeft, text)
                y_offset += 12
            painter.restore()

class FloatingCalendarWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.conn = sqlite3.connect("calendar_events.db")
        self.create_table()

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(500, 650)

        self.drag_position = None

        # Layout
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(8, 8, 8, 8)
        self.setLayout(self.layout)

        # Calendar
        self.calendar = EventCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        self.calendar.clicked.connect(self.load_event)
        self.layout.addWidget(self.calendar)

        # Event list
        self.events_list = QListWidget()
        self.events_list.setFixedHeight(130)
        self.events_list.itemClicked.connect(self.event_clicked)
        self.layout.addWidget(self.events_list)

        # Note editor
        self.note_label = QLabel("Event / Note:")
        self.note_label.setFont(QFont("Arial", 10, QFont.Bold))
        self.note_label.setStyleSheet("color: white;")
        self.layout.addWidget(self.note_label)

        self.note_area = QTextEdit()
        self.note_area.setFixedHeight(100)
        self.layout.addWidget(self.note_area)

        # Picker layout
        picker_layout = QHBoxLayout()

        self.colour_label = QLabel("Colour: None")
        self.colour_label.setStyleSheet("color: white; background-color: transparent; padding: 5px; border: 1px solid white;")
        picker_layout.addWidget(self.colour_label)

        self.pick_colour_btn = QPushButton("Pick Colour")
        self.pick_colour_btn.clicked.connect(self.pick_colour)
        picker_layout.addWidget(self.pick_colour_btn)

        self.icon_dropdown = QComboBox()
        self.icon_dropdown.addItems(["", "📅 Meeting", "🎂 Birthday", "⭐ Important", "💼 Work", "🛠 Personal"])
        picker_layout.addWidget(QLabel("Icon:"))
        picker_layout.addWidget(self.icon_dropdown)

        self.layout.addLayout(picker_layout)

        # Buttons
        self.save_btn = QPushButton("Add Event to Day")
        self.save_btn.clicked.connect(self.save_event)
        self.layout.addWidget(self.save_btn)

        self.delete_btn = QPushButton("Delete Selected Event")
        self.delete_btn.clicked.connect(self.delete_event)
        self.layout.addWidget(self.delete_btn)

        self.mini_btn = QPushButton("Toggle Mini Mode")
        self.mini_btn.clicked.connect(self.toggle_mini)
        self.layout.addWidget(self.mini_btn)

        self.close_btn = QPushButton("Close")
        self.close_btn.setStyleSheet("background-color: #a33; color: white;")
        self.close_btn.clicked.connect(self.close)
        self.layout.addWidget(self.close_btn)

        # Style
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(150, 20, 20, 220);
                color: white;
                font-family: Arial;
            }
            QPushButton {
                background-color: #444;
                border: none;
                padding: 6px;
                color: white;
            }
            QPushButton:hover {
                background-color: #666;
            }
            QComboBox {
                background-color: #333;
                color: white;
                padding: 3px;
            }
            QTextEdit {
                background-color: #222;
                color: white;
            }
        """)

        self.selected_date = None
        self.selected_colour = None
        self.selected_event_id = None
        self.mini_mode = False

        self.load_all_events()

    # ---- Database ----
    def create_table(self):
        c = self.conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                note TEXT,
                colour TEXT,
                icon TEXT
            )
        """)
        self.conn.commit()

    # ---- Event Management ----
    def pick_colour(self):
        colour = QColorDialog.getColor()
        if colour.isValid():
            self.selected_colour = colour.name()
            self.colour_label.setText(f"Colour: {self.selected_colour}")
            self.colour_label.setStyleSheet(f"color: white; background-color: {self.selected_colour}; padding: 5px; border: 1px solid white;")

    def load_event(self, date):
        self.selected_date = date.toString("yyyy-MM-dd")
        c = self.conn.cursor()
        c.execute("SELECT id, note, colour, icon FROM events WHERE date=?", (self.selected_date,))
        results = c.fetchall()
        self.events_list.clear()
        for id_, note, colour, icon in results:
            display_text = f"{icon} {note}"
            item = QListWidgetItem(display_text)
            if colour:
                item.setBackground(QColor(colour))
            item.setData(Qt.UserRole, id_)
            self.events_list.addItem(item)
        self.note_area.clear()
        self.selected_event_id = None
        self.selected_colour = None
        self.colour_label.setText("Colour: None")
        self.colour_label.setStyleSheet("color: white; background-color: transparent; padding: 5px; border: 1px solid white;")
        self.icon_dropdown.setCurrentIndex(0)

    def save_event(self):
        if not self.selected_date:
            QMessageBox.warning(self, "No Date Selected", "Please click a date first.")
            return
        note = self.note_area.toPlainText().strip()
        if not note:
            QMessageBox.warning(self, "Empty Note", "Event note cannot be empty.")
            return
        colour = self.selected_colour if self.selected_colour else ""
        icon = self.icon_dropdown.currentText()
        c = self.conn.cursor()
        c.execute("INSERT INTO events (date, note, colour, icon) VALUES (?, ?, ?, ?)",
                  (self.selected_date, note, colour, icon))
        self.conn.commit()
        self.load_event(QDate.fromString(self.selected_date, "yyyy-MM-dd"))
        self.load_all_events()
        QMessageBox.information(self, "Saved", "Event added successfully.")

    def event_clicked(self, item):
        event_id = item.data(Qt.UserRole)
        c = self.conn.cursor()
        c.execute("SELECT note, colour, icon FROM events WHERE id=?", (event_id,))
        result = c.fetchone()
        if result:
            note, colour, icon = result
            self.note_area.setPlainText(note)
            self.selected_colour = colour
            if colour:
                self.colour_label.setText(f"Colour: {colour}")
                self.colour_label.setStyleSheet(f"color: white; background-color: {colour}; padding: 5px; border: 1px solid white;")
            else:
                self.colour_label.setText("Colour: None")
                self.colour_label.setStyleSheet("color: white; background-color: transparent; padding: 5px; border: 1px solid white;")
            self.icon_dropdown.setCurrentText(icon if icon else "")
            self.selected_event_id = event_id

    def delete_event(self):
        selected_item = self.events_list.currentItem()
        if selected_item:
            event_id = selected_item.data(Qt.UserRole)
            response = QMessageBox.question(self, "Delete Event", "Delete this event?", QMessageBox.Yes | QMessageBox.No)
            if response == QMessageBox.Yes:
                c = self.conn.cursor()
                c.execute("DELETE FROM events WHERE id=?", (event_id,))
                self.conn.commit()
                self.load_event(QDate.fromString(self.selected_date, "yyyy-MM-dd"))
                self.load_all_events()
                self.note_area.clear()
                self.selected_colour = None
                self.selected_event_id = None
                self.colour_label.setText("Colour: None")
                self.colour_label.setStyleSheet("color: white; background-color: transparent; padding: 5px; border: 1px solid white;")
                self.icon_dropdown.setCurrentIndex(0)

    def load_all_events(self):
        c = self.conn.cursor()
        c.execute("SELECT date, note, colour, icon FROM events")
        events_dict = {}
        for date_str, note, colour, icon in c.fetchall():
            y, m, d = map(int, date_str.split('-'))
            qdate = QDate(y, m, d)
            if qdate not in events_dict:
                events_dict[qdate] = []
            events_dict[qdate].append((icon, note, colour))
        self.calendar.set_events(events_dict)

    # ---- Mini Mode ----
    def toggle_mini(self):
        if self.mini_mode:
            self.resize(500, 650)
            for w in (self.events_list, self.note_area, self.note_label,
                      self.colour_label, self.pick_colour_btn, self.icon_dropdown,
                      self.save_btn, self.delete_btn):
                w.show()
            self.mini_mode = False
        else:
            self.resize(300, 300)
            for w in (self.events_list, self.note_area, self.note_label,
                      self.colour_label, self.pick_colour_btn, self.icon_dropdown,
                      self.save_btn, self.delete_btn):
                w.hide()
            self.mini_mode = True

    # ---- Dragging ----
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_position:
            self.move(event.globalPos() - self.drag_position)
            event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FloatingCalendarWidget()
    window.show()

    # --- Always-on-bottom but clickable ---
    import ctypes
    from ctypes import wintypes
    SWP_NOMOVE = 0x0002
    SWP_NOSIZE = 0x0001
    SWP_NOACTIVATE = 0x0010
    HWND_BOTTOM = 1
    hwnd = int(window.winId())
    ctypes.windll.user32.SetWindowPos(hwnd, HWND_BOTTOM, 0, 0, 0, 0,
                                      SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE)

    sys.exit(app.exec_())
