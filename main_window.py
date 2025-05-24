from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QListWidget, QTextEdit, QLineEdit, QPushButton, QListWidgetItem,
    QMessageBox, QInputDialog, QDialog
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from models import User, Message, Group
from database import Database

class MainWindow(QMainWindow):
    def __init__(self, db, current_user):
        super().__init__()
        self.db = db 
        self.current_user = current_user
        self.current_chat = None
        self.is_group_chat = False
        self.init_ui()
        self.setup_timers()

    def init_ui(self):
            self.setWindowTitle(f"Messaging App-{self.current_user.first_name}")
            self.setGeometry(100,100,800,600)

            main_widget = QWidget()
            main_layout =QVBoxLayout()

            self.sidebar = QWidget()
            sidebar_layout = QVBoxLayout()

            self.contacts_label = QLabel("Online Users")
            sidebar_layout.addWidget(self.contacts_label)
            