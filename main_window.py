from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, QListWidget, QTextEdit, QMessageBox,
    QLineEdit, QPushButton, QListWidgetItem, QHBoxLayout, QStackedWidget
)
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, QPoint
from PyQt6.QtGui import QColor, QPalette
from models import User, Message, Group
from database import Database

class MainWindow(QMainWindow):
    def __init__(self, db, current_user):
        super().__init__()
        self.db = db
        self.current_user = current_user
        self.current_chat = None
        self.is_group_chat = False
        self.show_all_users = False  # Default: Show only online users

        self.init_ui()
        self.db.user_status_changed.connect(self.on_user_status_changed)
        self.load_users()
        self.load_groups()

    def init_ui(self):
        self.setWindowTitle(f"Messaging App - {self.current_user.first_name}")
        self.setGeometry(100, 100, 900, 600)

        self.setStyleSheet("""
            QListWidget {
                font-size: 14px;
                padding: 5px;
                border: none;
            }
            QLabel {
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton {
                padding: 6px 12px;
                font-size: 14px;
                border-radius: 6px;
                background-color: #0078d7;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background-color: #005fa3;
            }
            QLineEdit {
                font-size: 14px;
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 6px;
            }
            QTextEdit {
                font-size: 14px;
                background-color: #f9f9f9;
                border-radius: 6px;
                border: 1px solid #ddd;
            }
            QStackedWidget {
                background: white;
                border-radius: 8px;
            }
        """)

        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header with navigation buttons
        header = QWidget()
        header.setStyleSheet("background-color: #0078d7; padding: 10px;")
        header_layout = QHBoxLayout()
        
        self.users_btn = QPushButton("Users")
        self.users_btn.setCheckable(True)
        self.users_btn.setChecked(True)
        self.users_btn.clicked.connect(self.show_users_view)
        
        self.groups_btn = QPushButton("Groups")
        self.groups_btn.setCheckable(True)
        self.groups_btn.clicked.connect(self.show_groups_view)
        
        self.logout_btn = QPushButton("Logout")
        self.logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff4d4d;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d11a2a;
            }
        """)
        self.logout_btn.clicked.connect(self.handle_logout)
        
        header_layout.addWidget(self.users_btn)
        header_layout.addWidget(self.groups_btn)
        header_layout.addStretch()
        header_layout.addWidget(self.logout_btn)
        header.setLayout(header_layout)
        main_layout.addWidget(header)

        # Main content area with stacked widgets
        self.stacked_widget = QStackedWidget()
        
        # Users view
        self.users_widget = QWidget()
        users_layout = QVBoxLayout()
        
        users_top_bar = QHBoxLayout()
        self.contacts_label = QLabel("Online Users")
        self.toggle_button = QPushButton("Show All Users")
        self.toggle_button.clicked.connect(self.toggle_user_view)
        
        users_top_bar.addWidget(self.contacts_label)
        users_top_bar.addStretch()
        users_top_bar.addWidget(self.toggle_button)
        users_layout.addLayout(users_top_bar)
        
        self.contacts_list = QListWidget()
        self.contacts_list.itemClicked.connect(self.open_chat)
        users_layout.addWidget(self.contacts_list)
        
        self.users_widget.setLayout(users_layout)
        self.stacked_widget.addWidget(self.users_widget)

        # Groups view
        self.groups_widget = QWidget()
        groups_layout = QVBoxLayout()
        
        groups_top_bar = QHBoxLayout()
        self.groups_label = QLabel("Your Groups")
        self.create_group_btn = QPushButton("Create Group")
        self.create_group_btn.clicked.connect(self.create_group)
        
        groups_top_bar.addWidget(self.groups_label)
        groups_top_bar.addStretch()
        groups_top_bar.addWidget(self.create_group_btn)
        groups_layout.addLayout(groups_top_bar)
        
        self.groups_list = QListWidget()
        self.groups_list.itemClicked.connect(self.open_chat)
        groups_layout.addWidget(self.groups_list)
        
        self.groups_widget.setLayout(groups_layout)
        self.stacked_widget.addWidget(self.groups_widget)

        # Chat view
        self.chat_widget = QWidget()
        chat_layout = QVBoxLayout()
        
        chat_header = QHBoxLayout()
        self.chat_header = QLabel("Chat")
        self.back_btn = QPushButton("Back")
        self.back_btn.clicked.connect(self.show_previous_view)
        
        chat_header.addWidget(self.back_btn)
        chat_header.addWidget(self.chat_header)
        chat_header.addStretch()
        chat_layout.addLayout(chat_header)
        
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        chat_layout.addWidget(self.chat_display)
        
        input_layout = QHBoxLayout()
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Type your message here...")
        self.message_input.returnPressed.connect(self.send_message)
        
        self.send_btn = QPushButton("Send")
        self.send_btn.clicked.connect(self.send_message)
        
        input_layout.addWidget(self.message_input)
        input_layout.addWidget(self.send_btn)
        chat_layout.addLayout(input_layout)
        
        self.chat_widget.setLayout(chat_layout)
        self.stacked_widget.addWidget(self.chat_widget)

        main_layout.addWidget(self.stacked_widget)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Set initial view
        self.current_view = "users"
        self.previous_view = "users"

    def toggle_user_view(self):
        self.show_all_users = not self.show_all_users
        if self.show_all_users:
            self.contacts_label.setText("All Users")
            self.toggle_button.setText("Show Online Only")
        else:
            self.contacts_label.setText("Online Users")
            self.toggle_button.setText("Show All Users")
        self.load_users()

    def show_users_view(self):
        self.users_btn.setChecked(True)
        self.groups_btn.setChecked(False)
        self.switch_view("users")

    def show_groups_view(self):
        self.users_btn.setChecked(False)
        self.groups_btn.setChecked(True)
        self.switch_view("groups")

    def show_previous_view(self):
        self.switch_view(self.previous_view)
        if self.previous_view == "users":
            self.users_btn.setChecked(True)
            self.groups_btn.setChecked(False)
        else:
            self.users_btn.setChecked(False)
            self.groups_btn.setChecked(True)

    def switch_view(self, view_name):
        self.previous_view = self.current_view
        self.current_view = view_name
        
        if view_name == "users":
            target_index = 0
        elif view_name == "groups":
            target_index = 1
        else:  # chat
            target_index = 2
        
        self.animate_transition(target_index)

    def animate_transition(self, target_index):
        # Slide animation
        animation = QPropertyAnimation(self.stacked_widget, b"pos")
        animation.setDuration(300)
        animation.setEasingCurve(QEasingCurve.Type.OutQuad)
        
        current_pos = self.stacked_widget.pos()
        if target_index > self.stacked_widget.currentIndex():
            # Slide from right to left
            # animation.setStartValue(current_pos + QPoint(200, 0))
            # animation.setEndValue(current_pos)
            self.stacked_widget.setCurrentIndex(target_index)
        else:
            # Slide from left to right
            # animation.setStartValue(current_pos - QPoint(200, 0))
            # animation.setEndValue(current_pos)
            self.stacked_widget.setCurrentIndex(target_index)
        
        animation.start()

    def load_users(self):
        self.contacts_list.clear()
        users = self.db.get_all_users(exclude_user_id=self.current_user.id)

        sorted_users = sorted(users, key=lambda x: x[4], reverse=True)
        if not self.show_all_users:
            sorted_users = [u for u in sorted_users if u[4]]

        for user in sorted_users:
            user_id, first_name, last_name, email, is_online = user
            item = QListWidgetItem(f"{first_name} {last_name} {'🟢' if is_online else '⚪'}")
            item.setData(Qt.ItemDataRole.UserRole, (user_id, False))
            self.contacts_list.addItem(item)

    def load_groups(self):
        self.groups_list.clear()
        groups = self.db.get_user_groups(self.current_user.id)
        
        for group in groups:
            group_id, name, description = group
            item = QListWidgetItem(f"{name} - {description}")
            item.setData(Qt.ItemDataRole.UserRole, (group_id, True))
            self.groups_list.addItem(item)

    def open_chat(self, item):
        self.current_chat, self.is_group_chat = item.data(Qt.ItemDataRole.UserRole)
        
        if self.is_group_chat:
            self.chat_header.setText(f"Group: {item.text()}")
        else:
            self.chat_header.setText(f"Chat with {item.text()}")
        
        self.load_messages()
        self.switch_view("chat")

    def send_message(self):
        message_text = self.message_input.text().strip()
        if not message_text or not self.current_chat:
            return
            
        if self.is_group_chat:
            self.db.add_message(
                sender_id=self.current_user.id,
                group_id=self.current_chat,
                content=message_text
            )
        else:
            self.db.add_message(
                sender_id=self.current_user.id,
                receiver_id=self.current_chat,
                content=message_text
            )
        
        self.message_input.clear()
        self.load_messages()

    def load_messages(self):
        self.chat_display.clear()

        if self.is_group_chat:
            messages = self.db.get_group_messages(self.current_chat)
            for msg_data in messages:
                msg = Message(*msg_data[:7])
                sender_name = f"{msg_data[7]} {msg_data[8]}"
                self.append_message(sender_name, msg.content, msg.timestamp, msg.sender_id == self.current_user.id)
        else:
            messages = self.db.get_messages(self.current_user.id, self.current_chat)
            for msg_data in messages:
                msg = Message(*msg_data)
                sender_name = "You" if msg.sender_id == self.current_user.id else "Them"
                self.append_message(sender_name, msg.content, msg.timestamp, msg.sender_id == self.current_user.id)

        self.chat_display.verticalScrollBar().setValue(
            self.chat_display.verticalScrollBar().maximum()
        )

    def append_message(self, sender, content, timestamp, is_me):
        alignment = "right" if is_me else "left"
        color = "#DCF8C6" if is_me else "#ECECEC"

        html = f"""
        <div style='margin: 5px; text-align: {alignment};'>
            <div style='background: {color}; padding: 8px; border-radius: 8px; 
                        display: inline-block; max-width: 70%; word-wrap: break-word;'>
                <small><b>{sender}</b> - {timestamp}</small><br>
                {content}
            </div>
        </div>
        """
        self.chat_display.append(html)

    def create_group(self):
        # Implement group creation dialog
        pass

    def on_user_status_changed(self, user_id, is_online):
        if not self.show_all_users:
            self.load_users()

    def handle_logout(self):
        confirm = QMessageBox.question(self, "Logout", "Are you sure you want to logout?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if confirm == QMessageBox.StandardButton.Yes:
            self.db.update_user_status(self.current_user.id, False)
            self.close()

            if hasattr(self,"Login_signup"):
                self.Login_signup.login_email.clear()
                self.Login_signup.login_password.clear()
                self.Login_signup.show()