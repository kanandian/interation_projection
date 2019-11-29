import component
import sys
from PyQt5.QtWidgets import QApplication


def main():
    app = 0
    app = QApplication(sys.argv)
    application = component.Application()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()