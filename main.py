from PyQt6.QtWidgets import QApplication
from Login_signup import  Login_signup
from main_window import MainWindow
from database import Database
import sys

class MessagingApp:
    def __init__(self):
        self.db = Database()

        self.app = QApplication(sys.argv)
        self.login_signup = Login_signup(self.db,self.on_login_success)
        self.login_signup.show()
        sys.exit(self.app.exec())
    
    def on_login_success(self, user):
        self.login_signup.hide()
        self.mainwindow = MainWindow(self.db, user)
        self.mainwindow.show()
        print("sussess")
        

if __name__ == "__main__" :
    MessagingApp()