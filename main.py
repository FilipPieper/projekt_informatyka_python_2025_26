import sys
from PyQt5.QtWidgets import QApplication
from main_screen import MainScreen

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainScreen()
    w.show()
    sys.exit(app.exec_())
