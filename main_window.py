from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, QListWidget, QTextEdit,
    QLineEdit, QPushButton, QListWidgetItem, QHBoxLayout
)
from PyQt6.QtCore import Qt, pyqtSignal
from models import User, Message, Group
from database import Database

class MainWindow(QMainWindow):
    def __init__(self, db, current_user):
        super().__init__()
        self.db = db 
        self.current_user = current_user
        self.current_chat = None
        self.is_group_chat = False
        self.show_all_users = True  # Toggle state

        self.init_ui()

        self.db.user_status_changed.connect(self.on_user_status_changed)
        self.load_users()

    def init_ui(self):
        self.setWindowTitle(f"Messaging App - {self.current_user.first_name}")
        self.setGeometry(100, 100, 800, 600)

        main_widget = QWidget()
        main_layout = QHBoxLayout()

        # Sidebar
        self.sidebar = QWidget()
        sidebar_layout = QVBoxLayout()

        # Label + toggle
        top_bar = QHBoxLayout()
        self.contacts_label = QLabel("All Users")
        self.toggle_button = QPushButton("Switch to Online Users")
        self.toggle_button.clicked.connect(self.toggle_user_view)

        top_bar.addWidget(self.contacts_label)
        top_bar.addWidget(self.toggle_button)
        sidebar_layout.addLayout(top_bar)

        self.contacts_list = QListWidget()
        self.contacts_list.itemClicked.connect(self.switch_chat)
        sidebar_layout.addWidget(self.contacts_list)

        self.groups_label = QLabel("Your Groups")
        sidebar_layout.addWidget(self.groups_label)

        self.groups_list = QListWidget()
        self.groups_list.itemClicked.connect(self.switch_chat)
        sidebar_layout.addWidget(self.groups_list)

        self.sidebar.setLayout(sidebar_layout)

        # Chat Area
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

        # Main layout
        main_layout.addWidget(self.sidebar, stretch=1)
        main_layout.addWidget(self.chat_area, stretch=3)
        main_widget.setLayout(main_layout)

        self.setCentralWidget(main_widget)

    def toggle_user_view(self):
        self.show_all_users = not self.show_all_users
        if self.show_all_users:
            self.contacts_label.setText("All Users")
            self.toggle_button.setText("Switch to Online Users")
        else:
            self.contacts_label.setText("Online Users")
            self.toggle_button.setText("Switch to All Users")
        self.load_users()

    def load_users(self):
        self.contacts_list.clear()
        if self.show_all_users:
            users = self.db.get_all_users(exclude_user_id=self.current_user.id)
        else:
            users = self.db.get_online_users(exclude_user_id=self.current_user.id)

        for user in users:
            user_id, first_name, last_name, email = user
            item = QListWidgetItem(f"{first_name} {last_name}")
            item.setData(Qt.ItemDataRole.UserRole, (user_id, False))  # False means not group
            self.contacts_list.addItem(item)

    def switch_chat(self, item):
        chat_id, is_group = item.data(Qt.ItemDataRole.UserRole)
        self.current_chat = chat_id
        self.is_group_chat = is_group

        if is_group:
            self.chat_header.setText(f"Group: {item.text()}")
        else:
            self.chat_header.setText(f"Chat with {item.text()}")

    def send_message(self):
        pass  # You can implement this later

    def on_user_status_changed(self, user_id, is_online):
        if not self.show_all_users:
            self.load_users()
