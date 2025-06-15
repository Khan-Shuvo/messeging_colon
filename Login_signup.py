from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QMessageBox,
    QPushButton, QStackedWidget, QVBoxLayout, QFrame,
    QSizePolicy, QSpacerItem
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from models import User
import sys

class Login_signup(QMainWindow):
    def __init__(self, db, on_login_success):
        super().__init__()
        self.db = db
        self.on_login_success = on_login_success
        self.setWindowTitle("Login Form")
        self.setGeometry(100, 100, 400, 400)
        self.setStyleSheet("background-color: #2f2f2f;")
        self.main_ui()

    def main_ui(self):
        self.stak = QStackedWidget()

        # ------------------ Login Page ------------------
        login_page = QFrame()
        login_page.setStyleSheet("""
            QFrame {
                background-color: #000000;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        login_title = QLabel("Login")
        login_title.setFont(QFont("Arial", 20))
        login_title.setStyleSheet("color: white;")
        login_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.login_email = QLineEdit()
        self.login_email.setPlaceholderText("Email")
        self.login_email.setStyleSheet("padding: 10px; font-size: 14px; color: white;")

        self.login_password = QLineEdit()
        self.login_password.setPlaceholderText("Password")
        self.login_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.login_password.setStyleSheet("padding: 10px; font-size: 14px; color: white;")

        login_btn = QPushButton("Login")
        login_btn.setStyleSheet(self.button_style())
        login_btn.clicked.connect(self.handle_login)

        signup_btn = QPushButton("Signup")
        signup_btn.setStyleSheet(self.button_style())
        signup_btn.clicked.connect(lambda: self.stak.setCurrentIndex(1))  # switch to signup

        login_layout = QVBoxLayout()
        login_layout.addWidget(login_title)
        login_layout.addSpacing(10)
        login_layout.addWidget(self.login_email)
        login_layout.addSpacing(5)
        login_layout.addWidget(self.login_password)
        login_layout.addWidget(login_btn)
        login_layout.addWidget(signup_btn)

        login_page.setLayout(login_layout)

        # ------------------ Signup Page ------------------
        signup_page = QFrame()
        signup_page.setStyleSheet("""
            QFrame {
                background-color: #000000;
                border-radius: 10px;
                padding: 20px;
            }
        """)

        signup_title = QLabel("Signup")
        signup_title.setFont(QFont("Arial", 20))
        signup_title.setStyleSheet("color: white;")
        signup_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.signup_first_name = QLineEdit()
        self.signup_first_name.setPlaceholderText("First Name")
        self.signup_first_name.setStyleSheet("padding: 10px; font-size: 14px; color: white;")

        self.signup_last_name = QLineEdit()
        self.signup_last_name.setPlaceholderText("Last Name")
        self.signup_last_name.setStyleSheet("padding: 10px; font-size: 14px; color: white;")

        self.signup_email = QLineEdit()
        self.signup_email.setPlaceholderText("Email")
        self.signup_email.setStyleSheet("padding: 10px; font-size: 14px; color: white;")

        self.signup_password = QLineEdit()
        self.signup_password.setPlaceholderText("Password")
        self.signup_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.signup_password.setStyleSheet("padding: 10px; font-size: 14px; color: white;")

        self.signup_confirm = QLineEdit()
        self.signup_confirm.setPlaceholderText("Confirm Password")
        self.signup_confirm.setEchoMode(QLineEdit.EchoMode.Password)
        self.signup_confirm.setStyleSheet("padding: 10px; font-size: 14px; color: white;")

        register_btn = QPushButton("Register")
        register_btn.setStyleSheet(self.button_style())
        register_btn.clicked.connect(self.register_handel)

        back_btn = QPushButton("Back to Login")
        back_btn.setStyleSheet(self.button_style())
        back_btn.clicked.connect(lambda: self.stak.setCurrentIndex(0))  # switch to login

        signup_layout = QVBoxLayout()
        signup_layout.addWidget(signup_title)
        signup_layout.addSpacing(10)
        signup_layout.addWidget(self.signup_first_name)
        signup_layout.addWidget(self.signup_last_name)
        signup_layout.addWidget(self.signup_email)
        signup_layout.addWidget(self.signup_password)
        signup_layout.addWidget(self.signup_confirm)
        signup_layout.addWidget(register_btn)
        signup_layout.addWidget(back_btn)

        signup_page.setLayout(signup_layout)

        # ------------------ Add Pages to Stack ------------------
        self.stak.addWidget(login_page)   # index 0
        self.stak.addWidget(signup_page)  # index 1

        # ------------------ Container Layout ------------------
        container = QWidget()
        container_layout = QVBoxLayout()
        container_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        container_layout.addWidget(self.stak)
        container_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        container.setLayout(container_layout)

        self.setCentralWidget(container)

    def button_style(self):
        return """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                font-size: 14px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """
    
    def handle_login(self):
        email = self.login_email.text().strip()
        password = self.login_password.text().strip()

        if not email or not password:
            QMessageBox.warning(self,"Error","Please fill in all fields")
            return
        user_data = self.db.get_user_by_email(email)
        if not user_data :
            QMessageBox.warning(self, "Error", "User not found")
            return
        if user_data[4] != password:
            QMessageBox.warning(self, "Error","Incorrect password")
            return
        self.current_user = User(*user_data)
        self.on_login_success(self.current_user)

    def register_handel(self):
        first_name = self.signup_first_name.text().strip()
        last_name = self.signup_last_name.text().strip()
        email = self.signup_email.text().strip()
        password = self.signup_password.text().strip()
        confirm_password = self.signup_confirm.text().strip()

        if not all ([first_name, last_name, email, password, confirm_password]):
            QMessageBox.warning(self,"Error", "Please fill in all fields")
            return
        if password != confirm_password:
            QMessageBox.warning(self,"Error", "Password don't match")
        if self.db.get_user_by_email(email):
            QMessageBox.warning(self,"Error", "Email already Registered")
            return
        
        user_id = self.db.add_user(first_name, last_name, email, password)
        self.current_user = User(user_id, first_name, last_name, email,password,False, None)
        self.db.update_user_status(user_id, True)
        self.on_login_success(self.current_user)

