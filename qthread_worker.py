from PyQt5.QtCore import QThread, pyqtSignal
from web_crawler import WebCrawler
from PyQt5.QtWidgets import *

import time

# 컨텐츠를 가져오는 스레드
class GetContentsWorker(QThread):
    total_elements = 0
    signal = pyqtSignal(str, QThread, str, QTableWidget)

    def __init__(self, parent=None
                 , target_contents=None
                 , target_widget=None
                 , target_url=None
                 , user_id=None
                 , user_password=None
                 , duration=10):
        QThread.__init__(self, parent)
        self.target_contents = target_contents
        self.target_widget = target_widget
        self.target_url = target_url
        self.user_id = user_id
        self.user_password = user_password
        self.duration = duration

    def run(self):
        browser = WebCrawler()
        browser.login(self.user_id, self.user_password)

        while True:
            try:
                html = browser.get_page(self.target_url)

                # 로그인 세션이 끊기는 경우 재로그인 후 시도한다.
                if str(html.text) == '':
                    browser.login(self.user_id, self.user_password)
                    html = browser.get_page(self.target_url)

                self.signal.emit(self.target_contents, self, str(html.text), self.target_widget)
                time.sleep(self.duration)
            except Exception as e:
                print(e.args)


# 클라이언트에서 로그인 요청을 처리하는 스레드
class LoginWorker(QThread):
    signal = pyqtSignal(bool)

    def __init__(self, parent=None, user_id=None, user_password=None, duration=10):
        QThread.__init__(self, parent)
        self.user_id = user_id
        self.user_password = user_password
        self.duration = duration

    def run(self):
        result = False;
        browser = WebCrawler()

        try:
            browser.login(self.user_id, self.user_password)
            result = True
        except Exception:
            pass

        self.signal.emit(result)
