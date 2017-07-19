from PyQt5 import QtCore, QtWidgets
from PyQt5 import uic

import sys

# 알림 위젯 클래스
class NotiWidget(QtWidgets.QWidget):
    noti_count = 0
    win_list = []

    # 클래스 생성자 설정
    def __init__(self, message):
        super(NotiWidget, self).__init__()

        # 위제 윈도우 설정
        self.setWindowFlags(QtCore.Qt.SplashScreen | QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        # 위제 효과를 위한 애니메이션 등록
        self.animation = QtCore.QPropertyAnimation(self, b"windowOpacity", self)
        # self.animation.finished.connect(self.hide)
        self.timer = QtCore.QTimer()
        # self.timer.timeout.connect(self.hide_animation)

        # 알림 위젯 UI 파일 로드
        uic.loadUi("./ui/noti_widget.ui", self)

        # 알림 문구를 세팅함
        self.label.setText(message)
        self.label.setAlignment(QtCore.Qt.AlignCenter)

        self.pushButton_CLOSE.clicked.connect(self.btn_event_close)

        NotiWidget.noti_count = NotiWidget.noti_count + 1

    # 닫기 버튼
    def btn_event_close(self):
        self.hide_animation()

        for noti_win in NotiWidget.win_list:
            if noti_win == self:
                NotiWidget.win_list.remove(noti_win)

        for idx, noti_win in enumerate(NotiWidget.win_list):
            self.widget_relocation(noti_win, idx + 1)

    # 알림 위젯 출력 요청
    def show(self):
        self.setWindowOpacity(0.0)
        self.animation.setDuration(1500)
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        QtWidgets.QWidget.show(self)
        self.animation.start()
        self.timer.start(5000)

        NotiWidget.win_list.append(self)

        # 알림 위젯을 오른쪽 하단에 출력되도록 위치를 잡는다.
        self.set_right_bottom_corner(self)

    # 닫기 애니메이션 등록
    def hide_animation(self):
        NotiWidget.noti_count = NotiWidget.noti_count - 1

        QtWidgets.QWidget.hide(self)
        
    #  알림 위젯 닫기
    def hide(self):
        if self.windowOpacity() == 0:
            QtWidgets.QWidget.hide(self)

    # 알림 위젯 노티 위치를 설정
    def set_right_bottom_corner(self, win):
        try:
            screen_geometry = QtWidgets.QApplication.desktop().availableGeometry()
            screen_size = (screen_geometry.width(), screen_geometry.height())
            win_height = (win.frameSize().height() * NotiWidget.noti_count) + (NotiWidget.noti_count * 10)
            win_size = (win.frameSize().width(), win_height)
            x = screen_size[0] - win_size[0] - 10
            y = screen_size[1] - win_size[1] - 10
            win.move(x, y)
        except Exception as e:
            print(e)

    # 일림 위젯 닫기 버튼 누를 경우 재배치함
    def widget_relocation(self, win, idx):
        try:
            screen_geometry = QtWidgets.QApplication.desktop().availableGeometry()
            screen_size = (screen_geometry.width(), screen_geometry.height())
            win_height = (win.frameSize().height() * idx) + (idx * 10)
            win_size = (win.frameSize().width(), win_height)
            x = screen_size[0] - win_size[0] - 10
            y = screen_size[1] - win_size[1] - 10
            print(win, x, y)
            win.move(x, y)
        except Exception as e:
            print(e)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_window = NotiWidget('TEST')
    main_window.show()

    main_window1 = NotiWidget('TEST')
    main_window1.show()

    sys.exit(app.exec_())
