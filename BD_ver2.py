#!/usr/bin/env python3

import sqlite3 as db

import sys
from PyQt5.Qt import *
from PyQt5 import uic
from welcome import DBFormWindow

UI_Login_Form, Login_Form = uic.loadUiType("open.ui")

DB_login_PATH = "data.s3db"


class LoginWindow(Login_Form):
    def __init__(self, parent=None):
        # Инициализируем пользовательский интервейс // UI
        super(LoginWindow, self).__init__()
        self.ui = ui = UI_Login_Form()  # ui начинка окна
        ui.setupUi(self)
        # Подключение к событиям
        ui.enter.clicked.connect(self._check_user)
        # Подключение к бд
        self.conn = db.connect(DB_login_PATH)  # Исключительно в ОЗУ

    def __del__(self):  # деструктор
        self.ui = None  # теперь будет подобрано сборщиком мусора
        # Отключение от бд
        self.conn.close()

    def _check_user(self):
        # Вынимаем текст из lineEdit_username
        login = self.ui.lineEdit_username.text()
        # Вынимаем текст из lineEdit_password
        password = self.ui.lineEdit_password.text()
        # Пропускаем следующие шаги если пустой хотя бы одно из полей не заполнено
        if (not login) or (not password):
            msg = QMessageBox.information(self, 'Внимание!', 'Вы не заполнили все поля.')
            return
        # Пытаемся выполнить запрос
        cur = self.conn.cursor()
        try:  # две ветки
            # data = [('data', login)]
            # query = 'SELECT * FROM ? WHERE login = ?'
            query = 'SELECT * FROM data WHERE login = :login'
            # query = 'SELECT * FROM data WHERE login = ?'
            # query = ('SELECT * FROM data WHERE login = "' + login + '"').strip()
            cur.execute(query, {"login": login})
            # cur.execute(query, {"d": "data"})
            # cur.execute(query, [{"d": 'data'}, {"login": login}])
            self.conn.commit()  # сохраняем резальтат в базе
            result = cur.fetchone()
            if result == "" or result[1] != password:
                self.showMessageBox('Внимание!', 'Неправильное имя пользователя или пароль.')
                return
            error = None
        except Exception as exc:
            error = str(exc)
            self.showMessageBox('Внимание!', 'Неправильное имя пользователя или пароль.')
        cur.close()

        # Есть ошибка:
        if error is not None:
            print(error)
            #self.ui.error_label.setText(error)
        else:
            self.DBFormWindowShow()
            self.close()

    def showMessageBox(self, title, message):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Warning)
        msgBox.setWindowTitle(title)
        msgBox.setText(message)
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.exec_()

    def DBFormWindowShow(self):
        self.bdWindow = DBFormWindow()
        self.bdWindow.show()

    def keyPressEvent(self, event):
        if self.ui.lineEdit_password.hasFocus():
            if event.key() in (Qt.Key_Return, Qt.Key_Enter):  # Работать будет последовательным сравнением
                self._check_user()


if __name__ == "__main__":
    print("_____START PROGRAM_____")
    app = QApplication(sys.argv)  # экзепляр ядра приложения
    login_window = LoginWindow()  # экземпляр окошка
    login_window.show()
    sys.exit(app.exec_())  # код завершения отдаём sys
