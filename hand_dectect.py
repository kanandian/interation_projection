import cv2
import constant


class HandDectectByHandXML:
    def __init__(self):
        self.hand_cascade = cv2.CascadeClassifier(r'./resources/hand.xml')
        self.init_camera()

    def init_camera(self):
        self.vc = cv2.VideoCapture(0)  # 读入视频文件
        self.vc.set(3, constant.camera_width)  # 设置分辨率
        self.vc.set(4, constant.camera_height)

        rval, firstFrame = self.vc.read()
        # firstFrame = cv2.resize(firstFrame, (640, 360), interpolation=cv2.INTER_CUBIC)
        gray_firstFrame = cv2.cvtColor(firstFrame, cv2.COLOR_BGR2GRAY)  # 灰度化
        self.prveFrame = cv2.GaussianBlur(gray_firstFrame, (21, 21), 0)  # 高斯模糊，用于去噪
        self.prveFrame = self.prveFrame.copy()
        # print(firstFrame.shape)

    def get_hand_positions(self, mode):
        if mode == 1:
            return self.get_hand_positions_by_mode1()
        elif mode == 2:
            return self.get_hand_positions_by_mode2()

    def get_hand_positions_by_mode1(self):
        res = []
        # 探测图片中的人脸
        (ret, frame) = self.vc.read()
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        hands = self.hand_cascade.detectMultiScale(
            gray_frame,
            scaleFactor=1.15,
            minNeighbors=5,
            minSize=(5, 5)
        )
        for (x, y, w, h) in hands:
            res.append((x+w/2, y+w/2))
            cv2.circle(frame, ((x + x + w) // 2, (y + y + h) // 2), w // 2, (0, 255, 0), 2)

        if constant.show_camera:
            cv2.imshow('frame_with_result', cv2.flip(frame, 1, dst=None))
        return res

    def get_hand_positions_by_mode2(self):
        res = []
        (ret, frame) = self.vc.read()
        if not ret:
            return
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray_frame = cv2.GaussianBlur(gray_frame, (3, 3), 0)
        # 计算当前帧与上一帧的差别
        frameDiff = cv2.absdiff(self.prveFrame, gray_frame)
        if constant.show_camera:
            cv2.imshow("frameDiff", cv2.flip(frameDiff, 1, dst=None))
        self.prveFrame = gray_frame.copy()
        # 忽略较小的差别
        retVal, thresh = cv2.threshold(frameDiff, 100, 255, cv2.THRESH_BINARY)
        thresh = cv2.dilate(thresh, None, iterations=2)
        contours, hierarchy = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # 遍历轮廓
        for contour in contours:
            if cv2.contourArea(contour) < 1000:
                continue
            (x, y, w, h) = cv2.boundingRect(contour)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            centerx = x + w / 2
            centery = y + h / 2
            centerx *= constant.screen_width / constant.camera_width
            centery *= constant.screen_height / constant.camera_height
            res.append((x, y))

        if constant.show_camera:
            cv2.imshow('frame_with_result', cv2.flip(frame, 1, dst=None))

        return res