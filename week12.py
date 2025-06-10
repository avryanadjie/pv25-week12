import sys
import sqlite3
import csv
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QTextEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QComboBox, QTableWidget, QTableWidgetItem,
    QFileDialog, QStatusBar, QMenuBar, QAction, QDockWidget, QMessageBox, QScrollArea
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont

class MoodTracker(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mood & Daily Activity Tracker")
        self.setGeometry(100, 100, 900, 600)
        self.setupUI()
        self.createDatabase()
        self.loadData()

    def setupUI(self):
        # Menu bar
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")
        help_menu = menu_bar.addMenu("Help")

        export_csv_action = QAction("Export to CSV", self)
        export_csv_action.triggered.connect(self.exportToCSV)
        file_menu.addAction(export_csv_action)

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        about_action = QAction("About", self)
        about_action.triggered.connect(self.showAbout)
        help_menu.addAction(about_action)

        # Status bar
        status_bar = QStatusBar()
        status_bar.showMessage("Lalu Avryan Adjie Pratama | F1D021099")
        self.setStatusBar(status_bar)

        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        form_layout = QVBoxLayout()

        self.date_input = QLineEdit(QDate.currentDate().toString("yyyy-MM-dd"))
        self.date_input.setReadOnly(True)

        self.mood_input = QComboBox()
        self.mood_input.addItems(["Bahagia", "Biasa", "Stres", "Sedih"])

        self.activity_input = QLineEdit()
        self.note_input = QTextEdit()
        self.status_input = QLineEdit()

        save_button = QPushButton("Simpan")
        save_button.clicked.connect(self.saveData)
        save_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")

        form_layout.addWidget(QLabel("Tanggal:"))
        form_layout.addWidget(self.date_input)
        form_layout.addWidget(QLabel("Mood:"))
        form_layout.addWidget(self.mood_input)
        form_layout.addWidget(QLabel("Aktivitas:"))
        form_layout.addWidget(self.activity_input)
        form_layout.addWidget(QLabel("Catatan:"))
        form_layout.addWidget(self.note_input)
        form_layout.addWidget(QLabel("Status:"))
        form_layout.addWidget(self.status_input)
        form_layout.addWidget(save_button)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Tanggal", "Mood", "Aktivitas", "Catatan", "Status"])
        self.table.setStyleSheet("alternate-background-color: #f0f0f0; background-color: #fff;")
        self.table.setAlternatingRowColors(True)

        # Scroll area
        scroll_area = QScrollArea()
        form_widget = QWidget()
        form_widget.setLayout(form_layout)
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(form_widget)

        layout = QVBoxLayout()
        layout.addWidget(scroll_area)
        layout.addWidget(self.table)

        main_widget.setLayout(layout)

        # Dock widget (search bar)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cari berdasarkan aktivitas...")
        self.search_input.textChanged.connect(self.searchData)

        dock = QDockWidget("Pencarian", self)
        dock.setWidget(self.search_input)
        dock.setFloating(False)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)

    def createDatabase(self):
        self.conn = sqlite3.connect("mood_data.db")
        self.c = self.conn.cursor()
        self.c.execute('''CREATE TABLE IF NOT EXISTS mood (
                            tanggal TEXT,
                            mood TEXT,
                            aktivitas TEXT,
                            catatan TEXT,
                            status TEXT)''')
        self.conn.commit()

    def saveData(self):
        data = (
            self.date_input.text(),
            self.mood_input.currentText(),
            self.activity_input.text(),
            self.note_input.toPlainText(),
            self.status_input.text()
        )
        self.c.execute("INSERT INTO mood VALUES (?, ?, ?, ?, ?)", data)
        self.conn.commit()
        self.loadData()
        self.clearForm()

    def loadData(self):
        self.c.execute("SELECT * FROM mood")
        records = self.c.fetchall()
        self.table.setRowCount(len(records))
        for row_idx, row_data in enumerate(records):
            for col_idx, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))
                # Highlight row color by mood
                if col_idx == 1:
                    mood = value.lower()
                    if "stres" in mood:
                        item.setBackground(Qt.red)
                    elif "bahagia" in mood:
                        item.setBackground(Qt.green)
                    elif "sedih" in mood:
                        item.setBackground(Qt.yellow)
                self.table.setItem(row_idx, col_idx, item)

    def clearForm(self):
        self.activity_input.clear()
        self.note_input.clear()
        self.status_input.clear()

    def searchData(self):
        keyword = self.search_input.text().lower()
        self.c.execute("SELECT * FROM mood")
        records = self.c.fetchall()
        filtered = [r for r in records if keyword in r[2].lower()]  # Search in aktivitas
        self.table.setRowCount(len(filtered))
        for row_idx, row_data in enumerate(filtered):
            for col_idx, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))
                self.table.setItem(row_idx, col_idx, item)

    def exportToCSV(self):
        path, _ = QFileDialog.getSaveFileName(self, "Simpan File CSV", "", "CSV Files (*.csv)")
        if path:
            self.c.execute("SELECT * FROM mood")
            records = self.c.fetchall()
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Tanggal", "Mood", "Aktivitas", "Catatan", "Status"])
                writer.writerows(records)
            QMessageBox.information(self, "Sukses", "Data berhasil diekspor ke CSV!")

    def showAbout(self):
        QMessageBox.information(self, "Tentang Aplikasi", "Mood & Daily Activity Tracker\nDibuat oleh: Lalu Avryan Adjie Pratama\nNIM: F1D021099")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MoodTracker()
    window.show()
    sys.exit(app.exec_())
