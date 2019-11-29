import constant
import random
import mthread
import math
import hand_dectect
from PyQt5.QtWidgets import QMainWindow, QLabel
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QBasicTimer, QRect


class Leaf:
    def __init__(self):
        self.pixmap = QPixmap('images/yezi.png')
        self.label = 0
        self.position_x = float(random.randint(0, constant.screen_width))
        self.position_y = float(0)
        self.rect = QRect(int(self.position_x), int(self.position_y), constant.leaf_width, constant.leaf_height)
        self.dirction_x = -1
        self.dirction_y = -1
        self.speed = constant.move_speed

    def check_edges(self, geometry):

        if self.rect.right() < 0 or self.rect.left() > geometry.width() or self.rect.bottom() < 0 or self.rect.top() > geometry.height():
            return True
        return False

    def update(self):
        if self.dirction_x == -1 and self.dirction_y == -1:
            self.position_y += self.speed
        else:
            if self.dirction_x != -1:
                self.position_x += self.dirction_x
            if self.dirction_y != -1:
                self.position_y += self.dirction_y

        self.label.move(self.position_x, self.position_y)
        self.rect.setX(self.position_x)
        self.rect.setY(self.position_y)


class Application(QMainWindow):
    def __init__(self):
        super().__init__()

        self.leaves = []
        self.backgound_color = constant.background_color
        self.hand_dectect = hand_dectect.HandDectect()

        self.initUI()
        self.initTimer()
        self.startThreads()

    def initUI(self):
        #添加初始叶子
        for i in range(0,constant.initial_leaves_num):
            self.add_leaf()

        self.setGeometry(0, 0 , constant.screen_width, constant.screen_height)
        self.setWindowTitle('interation_projection')
        self.show()

    def initTimer(self):
        self.timer = QBasicTimer()
        self.timer.start(20, self)

    def startThreads(self):
        self.add_leaf_thread = mthread.AddLeafThread(self)
        self.add_leaf_thread.addLeafSingal.connect(self.add_leaf)
        self.add_leaf_thread.start()

    # 重写关闭应用事件
    def closeEvent(self, event):
        self.add_leaf_thread.running = False
        self.hand_dectect.vc.release()

    def timerEvent(self, event):
        if event.timerId() == self.timer.timerId():
            self.handle_hand_motion_by_mode()
            # self.capture_and_handle_frame()
            self.update_leaves()
            self.remove_invalid_leaves()
            self.update()

        else:
            super(Application, self).timerEvent(event)

    def handle_hand_motion_by_mode(self):
        positions = self.hand_dectect.get_hand_positions(constant.dectect_mod)
        for (x, y) in positions:
            x *= constant.screen_width / constant.camera_width
            y *= constant.screen_height / constant.camera_height
            x = constant.screen_width - x
            self.sweep_at(x, y)

    def update_leaves(self):
        for leaf in self.leaves:
            leaf.update()

    def add_leaf(self):
        leaf = Leaf()

        label = QLabel(self)
        label.setPixmap(leaf.pixmap)
        label.setGeometry(leaf.position_x, leaf.position_y, leaf.rect.width(), leaf.rect.height())
        label.setScaledContents(True)

        leaf.label = label

        label.show()

        self.leaves.append(leaf)

    def remove_invalid_leaves(self):
        for leaf in self.leaves:
            if leaf.check_edges(self.geometry()):
                self.leaves.remove(leaf)

    def sweep_at(self, x, y):
        fa = False
        fb = False
        for leaf in self.leaves:
            dist_x = leaf.rect.center().x()-x
            dist_y = leaf.rect.center().y()-y
            distance = math.sqrt(math.pow(dist_x, 2) + math.pow(dist_y, 2))
            if distance < constant.max_distance:
                leaf.speed = constant.sweep_speed
                if dist_x < 0:
                    fa = True
                if dist_y < 0:
                    fb = True
                if dist_x == 0:
                    leaf.dirction_x = -1
                    leaf.dirction_y = leaf.speed
                    if fb:
                        leaf.dirction_y *= -1
                else:
                    b = math.fabs(float(dist_y)/float(dist_x))
                    a = leaf.speed/math.sqrt(1+b*b)
                    b *= a
                    if fa:
                        a *= -1
                    if fb:
                        b *= -1
                    leaf.dirction_x = a
                    leaf.dirction_y = b
