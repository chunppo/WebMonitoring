from PyQt5.QtWidgets import *
from PyQt5 import uic
from bs4 import BeautifulSoup as bs
from PyQt5.QtGui import QIcon

from noti_widget import NotiWidget
from qthread_worker import GetContentsWorker
from qthread_worker import LoginWorker

import sys
import time
import json

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        uic.loadUi("./ui/login_form.ui", self)
        self.show()

        self.setTabOrder(self.lineEdit_ID, self.lineEdit_PW)
        self.setTabOrder(self.lineEdit_PW, self.pushButton_LOGIN)

        self.lineEdit_PW.setEchoMode(QLineEdit.Password)
        self.pushButton_LOGIN.clicked.connect(self.btn_event_login)

    def btn_event_login(self):
        self.line_id = self.lineEdit_ID.text()
        self.line_pw = self.lineEdit_PW.text()

        if self.line_id == '' or self.line_pw == '':
            QMessageBox.information(self, "알림", "ID 또는 PW를 입력하세요!")
        else:
            self.login_worker = LoginWorker(
                user_id=self.line_id,
                user_password=self.line_pw,
                duration=4)
            self.login_worker.signal.connect(self.login_worker_emit)
            self.login_worker.start()

    def login_worker_emit(self, login_flag):
        if login_flag:
            self.change_main_form()
        else:
            QMessageBox.information(self, "알림", "ID 또는 PW가 틀립니다.")
            return

    def change_main_form(self):
        uic.loadUi("./ui/main_form.ui", self)
        self.show()

        # Tag Contents Update QThread Worker
        self.get_tag_contents_worker = GetContentsWorker(
            target_contents='contents',
            target_widget=self.tableWidget_SQUARE,
            target_url='URL',
            user_id=self.line_id, user_password=self.line_pw, duration=60)
        self.get_tag_contents_worker.signal.connect(self.get_contents_worker_emit)
        self.get_tag_contents_worker.start()

        # Notice Contents Update QThread Worker
        self.get_notice_contents_worker = GetContentsWorker(
            target_contents='title',
            target_widget=self.tableWidget_NOTICE,
            target_url='URL',
            user_id=self.line_id, user_password=self.line_pw, duration=180)
        self.get_notice_contents_worker.signal.connect(self.get_contents_worker_emit)
        self.get_notice_contents_worker.start()

    def send_notification(self, notification_message):
        main_window = NotiWidget(notification_message)
        main_window.show()

    # Contents Update QThread Worker
    def get_contents_worker_emit(self, contents, cls, item, widget):
        self.lineEdit_TIME.setText(time.strftime('%Y.%m.%d %H:%M:%S', time.localtime()))

        dict_from_json = json.loads(item)

        # row, column 갯수 설정해야만 tablewidget 사용할수있다.
        widget.setColumnCount(4)
        widget.setRowCount(int(dict_from_json['size']))

        # column header 명 설정.
        widget.setHorizontalHeaderLabels(['ID', '작성자', '내용', '작성일'])

        if cls.total_elements == 0:
            cls.total_elements = dict_from_json['totalElements']

            self.setup_contents(contents, dict_from_json, widget)
        else:
            if dict_from_json['totalElements'] > cls.total_elements:
                cls.total_elements = dict_from_json['totalElements']

                page_html = bs(dict_from_json['content'][0][contents], 'html.parser')
                self.send_notification(page_html.text[0:60])

                self.setup_contents(contents, dict_from_json, widget)

    # 태그 컨텐츠를 테이블위젯에 출력한다.
    def setup_contents(self, contents, dict_from_json, widget):
        try:
            for idx, line in enumerate(dict_from_json['content']):
                widget.setRowHeight(idx, 50)
                widget.setColumnWidth(0, 50)
                widget.setColumnWidth(1, 60)
                widget.setColumnWidth(2, 500)
                widget.setColumnWidth(3, 120)

                widget.setItem(idx, 0, QTableWidgetItem(str(line['id'])))
                widget.setItem(idx, 1, QTableWidgetItem(line['user']['name']))
                text_edit = QTextEdit()

                page_html = bs(str(line[contents]), 'html.parser')
                text_edit.setText(page_html.text)
                widget.setCellWidget(idx, 2, text_edit)

                create_date = time.strftime('%Y.%m.%d %H:%M', time.localtime(int(line['createDate']) / 1000))
                widget.setItem(idx, 3, QTableWidgetItem(create_date))
        except Exception as e:
            print(e.args)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('./images/favicon.ico'))
    myWindow = MainWindow()
    myWindow.show()
    sys.exit(app.exec_())
