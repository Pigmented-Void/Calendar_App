import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QCalendarWidget, QTextEdit, QPushButton,
    QMessageBox, QHBoxLayout, QLabel, QComboBox, QListWidget, QListWidgetItem, QSizePolicy, QSpacerItem
)
from PyQt5.QtGui import QTextCharFormat, QColor, QFont
from PyQt5.QtCore import Qt, QDate, QRectF

ICON_COLOR_MAP = {
    "📅 Meeting": "#1E90FF",  # DodgerBlue
    "🎂 Birthday": "#FF69B4",  # HotPink
    "⭐ Important": "#FFD700",  # Gold
    "💼 Work": "#32CD32",      # LimeGreen
    "🛠 Personal": "#FF8C00"   # DarkOrange
}

class EventCalendarWidget(QCalendarWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.events_by_date = {}
        self.init_styles()

        # Set fixed size of calendar to control cell size indirectly
        # You can adjust these numbers to get desired cell size
        self.setFixedSize(720, 600)

        # Font sizes to control cell size visually
        self.setFont(QFont("Ebrima", 10))

        # Customize day of week header height and day cell height via style sheet
        # Note: This can vary depending on Qt version and platform
        self.setStyleSheet("""
            /* Header (day of week) */
            QCalendarWidget QTableView QWidget {
                min-height: 40px;   /* header row height */
            }
            /* Cells */
            QCalendarWidget QWidget#qt_calendar_calendarview {
                font-size: 14px;
                min-height: 40px;
            }
        """)

    def init_styles(self):
        header_font = QFont("Ebrima", 20, QFont.Bold)

        weekday_format = QTextCharFormat()
        weekday_format.setFont(header_font)
        weekday_format.setForeground(QColor("#27033A"))

        weekend_format = QTextCharFormat()
        weekend_format.setFont(header_font)
        weekend_format.setForeground(QColor("#026694"))

        for day in (Qt.Monday, Qt.Tuesday, Qt.Wednesday, Qt.Thursday, Qt.Friday):
            self.setWeekdayTextFormat(day, weekday_format)
        self.setWeekdayTextFormat(Qt.Saturday, weekend_format)
        self.setWeekdayTextFormat(Qt.Sunday, weekend_format)

    def set_events(self, events_dict):
        self.events_by_date = events_dict
        self.update()

    def paintCell(self, painter, rect, date):
        painter.save()

        if date == QDate.currentDate():
            painter.fillRect(rect, QColor(60, 60, 60, 180))
        elif date.dayOfWeek() in (6, 7):
            painter.fillRect(rect, QColor(60, 38, 84, 100))

        date_font = QFont("Ebrima", 13, QFont.Bold)
        painter.setFont(date_font)

        if date == QDate.currentDate():
            painter.setPen(QColor("#03A06B"))
        else:
            painter.setPen(QColor("#FFFFFF"))

        painter.drawText(rect.x() + 6, rect.y() + 18, str(date.day()))

        if date in self.events_by_date:
            event_font = QFont("Segoe UI", 9)
            painter.setFont(event_font)
            y_offset = rect.y() + 38
            padding_x = 3
            padding_y = 2
            text_height = 12
            for icon, note, colour in self.events_by_date[date][:3]:
                bg_colour = ICON_COLOR_MAP.get(icon, "#555555")
                painter.setBrush(QColor(bg_colour))
                painter.setPen(Qt.NoPen)

                text = f"{icon} {note}" if icon else note
                text_width = painter.fontMetrics().boundingRect(text).width()
                rect_bg = QRectF(rect.x() + padding_x, y_offset - text_height + padding_y, text_width + 8, text_height + 6)

                painter.drawRoundedRect(rect_bg, 4, 4)

                painter.setPen(QColor("#FFFFFF"))
                painter.drawText(
                    int(rect_bg.x() + padding_x),
                    int(rect_bg.y() + text_height + padding_y - 2),
                    text
                )

                y_offset += 18

        painter.restore()


class FloatingCalendarWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.conn = sqlite3.connect("calendar_events.db")
        self.create_table()

        # Set frameless & translucent window
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(720, 900)

        self.drag_position = None

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(12, 12, 12, 12)
        self.layout.setSpacing(12)
        self.setLayout(self.layout)

        self.calendar = EventCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        self.calendar.clicked.connect(self.load_event)
        self.layout.addWidget(self.calendar)

        self.events_list = QListWidget()
        self.events_list.setFixedHeight(130)
        self.events_list.itemClicked.connect(self.event_clicked)
        self.layout.addWidget(self.events_list)

        self.note_label = QLabel("Event / Note:")
        self.note_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.note_label.setStyleSheet("color: white; margin-bottom: 4px;")
        self.layout.addWidget(self.note_label)

        self.note_area = QTextEdit()
        self.note_area.setFixedHeight(110)
        self.layout.addWidget(self.note_area)

        picker_layout = QHBoxLayout()
        picker_layout.setSpacing(15)

        self.icon_dropdown = QComboBox()
        self.icon_dropdown.addItems(["", "📅 Meeting", "🎂 Birthday", "⭐ Important", "💼 Work", "🛠 Personal"])
        self.icon_dropdown.setFixedWidth(150)
        picker_layout.addWidget(QLabel("Icon:"))
        picker_layout.addWidget(self.icon_dropdown)

        picker_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.layout.addLayout(picker_layout)

        # Buttons layout
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(20)

        self.save_btn = QPushButton("Add Event to Day")
        self.save_btn.setFixedSize(150, 35)
        self.save_btn.clicked.connect(self.save_event)
        btn_layout.addWidget(self.save_btn)

        self.delete_btn = QPushButton("Delete Selected Event")
        self.delete_btn.setFixedSize(150, 35)
        self.delete_btn.clicked.connect(self.delete_event)
        btn_layout.addWidget(self.delete_btn)

        self.mini_btn = QPushButton("Toggle Mini Mode")
        self.mini_btn.setFixedSize(150, 35)
        self.mini_btn.clicked.connect(self.toggle_mini)
        btn_layout.addWidget(self.mini_btn)

        self.close_btn = QPushButton("Close")
        self.close_btn.setFixedSize(150, 35)
        self.close_btn.setStyleSheet("background-color: #a33; color: white;")
        self.close_btn.clicked.connect(self.close)
        btn_layout.addWidget(self.close_btn)

        self.layout.addLayout(btn_layout)

        self.setStyleSheet("""
            QWidget {
                background-color: rgba(29, 28, 36, 0.81);
                color: white;
                font-family: Ebrima;
            }
            QPushButton {
                background-color: #444;
                border: none;
                padding: 6px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #666;
            }
            QComboBox {
                background-color: #333;
                color: white;
                padding: 5px;
                font-size: 12pt;
            }
            QTextEdit {
                background-color: #222;
                color: white;
                font-size: 12pt;
            }
            QLabel {
                font-size: 12pt;
            }
        """)

        self.selected_date = None
        self.selected_event_id = None

        self.load_all_events()

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

    def load_event(self, date):
        self.selected_date = date.toString("yyyy-MM-dd")
        c = self.conn.cursor()
        c.execute("SELECT id, note, colour, icon FROM events WHERE date=?", (self.selected_date,))
        results = c.fetchall()
        self.events_list.clear()
        for id_, note, colour, icon in results:
            display_text = f"{icon} {note}"
            item = QListWidgetItem(display_text)
            bg_colour = ICON_COLOR_MAP.get(icon, None)
            if bg_colour:
                item.setBackground(QColor(bg_colour))
            item.setData(Qt.UserRole, id_)
            self.events_list.addItem(item)
        self.note_area.clear()
        self.selected_event_id = None
        self.icon_dropdown.setCurrentIndex(0)

    def save_event(self):
        if not self.selected_date:
            QMessageBox.warning(self, "No Date Selected", "Please click a date first.")
            return
        note = self.note_area.toPlainText().strip()
        if not note:
            QMessageBox.warning(self, "Empty Note", "Event note cannot be empty.")
            return
        icon = self.icon_dropdown.currentText()
        colour = ICON_COLOR_MAP.get(icon, "")
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
                self.selected_event_id = None
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

    def toggle_mini(self):
        if hasattr(self, "mini_mode") and self.mini_mode:
            self.resize(720, 900)
            for w in (self.events_list, self.note_area, self.note_label,
                      self.icon_dropdown, self.save_btn, self.delete_btn,
                      self.mini_btn, self.close_btn):
                w.show()
            self.mini_mode = False
        else:
            self.resize(320, 350)
            for w in (self.events_list, self.note_area, self.note_label,
                      self.icon_dropdown, self.save_btn, self.delete_btn,
                      self.mini_btn, self.close_btn):
                w.hide()
            self.mini_mode = True

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

    import ctypes
    SWP_NOMOVE = 0x0002
    SWP_NOSIZE = 0x0001
    SWP_NOACTIVATE = 0x0010
    HWND_BOTTOM = 1
    hwnd = int(window.winId())
    ctypes.windll.user32.SetWindowPos(hwnd, HWND_BOTTOM, 0, 0, 0, 0,
                                      SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE)

    sys.exit(app.exec_())
