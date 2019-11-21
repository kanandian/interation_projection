import time
import constant
from PyQt5.QtCore import QThread, pyqtSignal


class AddLeafThread(QThread):
    addLeafSingal = pyqtSignal()

    def __init__(self, parent = None):
        super().__init__(parent)
        self.running = True

    def run(self):
        while self.running:
            self.addLeafSingal.emit()
            time.sleep(constant.add_leaf_speed_factor)

