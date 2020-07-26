from PyQt5.Qt import *
from PyQt5 import uic
import sqlite3 as db
import sys

#TODO разобраться как сделать открытие нескольких таблиц одновременно
from table_window import TableWindow

DB_PATH = "fin_bd.s3db"
UI_DB_Form, DB_Form = uic.loadUiType("db_select.ui")

conn = db.connect(DB_PATH)
cursor = conn.execute("SELECT * FROM sqlite_master where type = 'table'")
result = cursor.fetchall()
conn.close()
table_names = []
for item in result:
    table_names.append(item[1])


class DBFormWindow(DB_Form):
    def __init__(self, parent=None):
        DB_Form.__init__(self, parent)
        self.ui = UI_DB_Form()
        self.ui.setupUi(self)
        self.ui.streams_button.clicked.connect(self._streams)
        self.ui.students_button.clicked.connect(self._students)
        self.ui.exams_button.clicked.connect(self._exams)
        self.ui.sessions_button.clicked.connect(self._sessions)
        self.ui.departments_button.clicked.connect(self._departments)

    def _streams(self):
        self.bdWindow = TableWindow(1)
        self.bdWindow.show()

    def _students(self):
        self.bdWindow = TableWindow(0)
        self.bdWindow.show()

    def _exams(self):
        self.bdWindow = TableWindow(2)
        self.bdWindow.show()

    def _sessions(self):
        self.bdWindow = TableWindow(4)
        self.bdWindow.show()

    def _departments(self):
        self.bdWindow = TableWindow(3)
        self.bdWindow.show()

    def __del__(self):
        self.ui = None


if __name__ == "__main__":
    print(table_names)
    app = QApplication(sys.argv)
    w = DBFormWindow()
    w.show()
    sys.exit(app.exec_())
