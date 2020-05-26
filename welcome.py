from PyQt5.Qt import *
from PyQt5 import uic
import sqlite3 as db
import sys

from streams import StreamsWindow
from students import StudentsWindow
from exams import ExamsWindow
from sessions import SessionsWindow
from departments import DepartmentsWindow

UI_DB_Form, DB_Form = uic.loadUiType("db_select.ui")


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
        self.bdWindow = StreamsWindow()
        self.bdWindow.show()

    def _students(self):
        self.bdWindow = StudentsWindow()
        self.bdWindow.show()

    def _exams(self):
        self.bdWindow = ExamsWindow()
        self.bdWindow.show()

    def _sessions(self):
        self.bdWindow = SessionsWindow()
        self.bdWindow.show()

    def _departments(self):
        self.bdWindow = DepartmentsWindow()
        self.bdWindow.show()

    def __del__(self):
        self.ui = None


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = DBFormWindow()
    w.show()
    sys.exit(app.exec_())
