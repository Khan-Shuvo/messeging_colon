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
        # self.setup_timers()

    def init_ui(self):
            self.setWindowTitle(f"Messaging App-{self.current_user.first_name}")
            self.setGeometry(100,100,800,600)

            main_widget = QWidget()
            main_layout =QHBoxLayout()

            self.sidebar = QWidget()
            sidebar_layout = QVBoxLayout()

            self.contacts_label = QLabel("Online Users")
            sidebar_layout.addWidget(self.contacts_label)

            self.contacts_list = QListWidget()
            self.contacts_list.itemClicked.connect(self.switch_chat)
            sidebar_layout.addWidget(self.contacts_list)

            self.groups_label = QLabel("Your Groups")
            sidebar_layout.addWidget(self.groups_label)

            self.groups_list = QListWidget()
            self.groups_list.itemClicked.connect(self.switch_chat)
            sidebar_layout.addWidget(self.groups_list)
            
            self.sidebar.setLayout(sidebar_layout)
            
            self.chat_area = QWidget()
            chat_layout = QVBoxLayout()
            
            self.chat_header = QLabel("Select a chat to start messaging")
            self.chat_header.setStyleSheet("font-size: 16px; font-weight: bold;")
            chat_layout.addWidget(self.chat_header)
            
            self.chat_display = QTextEdit()
            self.chat_display.setReadOnly(True)
            chat_layout.addWidget(self.chat_display)
            
            self.message_input = QLineEdit()
            self.message_input.setPlaceholderText("Type your message here...")
            self.message_input.returnPressed.connect(self.send_message)
            chat_layout.addWidget(self.message_input)
            
            self.send_btn = QPushButton("Send")
            self.send_btn.clicked.connect(self.send_message)
            chat_layout.addWidget(self.send_btn)
            
            self.chat_area.setLayout(chat_layout)
            
            main_layout.addWidget(self.sidebar, stretch=1)
            main_layout.addWidget(self.chat_area, stretch=3)
            main_widget.setLayout(main_layout)
            
            self.setCentralWidget(main_widget)
            


    def switch_chat(self, item):
        chat_id, is_group = item.data(Qt.ItemDataRole.UserRole)
        self.current_chat = chat_id
        self.is_group_chat = is_group

        if is_group:
             self.chat_header.setText(f"Group: {item.text()}")
        else:
             user_name = item.text()
             self.chat_header.setText(f"Chat with {user_name}")


    def send_message(self):
         pass
        