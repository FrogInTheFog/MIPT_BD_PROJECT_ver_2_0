from PyQt5.Qt import *
from PyQt5 import QtCore, QtWidgets
import sqlite3 as db
import sys
import os
from os import listdir
from os.path import join, isfile


class LoginDatabase():
    def __init__(self, db_path):
        if db_path != '':  # если мы указываем бд
            self.dbname = db_path
            self.conn = db.connect(self.dbname)
            self.table_names = self.get_tables()
        else:  # необходимо для инициализации
            self.dbname = ''
            self.table_names = []
            print("База данных не выбрана. Соединение не установлено. Список таблиц пуст")

    def get_tables(self):
        cursor = self.conn.execute("SELECT * FROM sqlite_master where type = 'table'")
        result = cursor.fetchall()
        table_names = []
        for item in result:
            table_names.append(item[1])
        return table_names

    def tables_names(self, table):  # выводит наименование столбцов
        query = "SELECT * FROM " + table + ";"
        cursor = self.conn.execute(query)
        result = cursor.description
        return result

    def select_all_query(self, table):  # выводит всю бд
        query = "SELECT * FROM " + table + ";"
        cursor = self.conn.execute(query)
        result = cursor.fetchall()
        return result

    def count_strings(self, table):  # выводит количество записей // строк
        query = "SELECT COUNT(*) FROM " + table + ";"
        cursor = self.conn.execute(query)
        result = cursor.fetchone()
        return result[0]

    def show_date(self, table):  # выводит всю таблицу
        query = "SELECT * FROM " + table + ";"
        cursor = self.conn.execute(query)
        result = cursor.fetchall()
        return result

    def sort(self, table, column_name):  # сортировка
        query = "SELECT * FROM " + table + " ORDER BY " + str(column_name)
        print(query, column_name)
        cursor = self.conn.execute(query)
        result = cursor.fetchall()
        self.conn.commit()
        return result

    def getPK(self, table):
        # Необходим метод, который возвращает наименование столбца, который является Primary Key  этой таблице
        return

    def update_date(self, table, new_data, new_columns_names):  # обновляет таблицу
        new_cols = new_columns_names
        cur_data = self.select_all_query(table)
        columns_name = self.tables_names(table)  # Получаем список колон
        # print("Длинна старых данных " + str(len(columns_name)))
        # print("Длинна новых данных " + str(len(new_data[0])))
        if str(len(columns_name)) == str(len(new_data[0])):  # Если новых столбцов не было
            result_headers = ""
            for column_description in columns_name:
                result_headers += column_description[0] + " "
            list_result_headers = result_headers[0:(len(result_headers) - 1)].split(" ")
            map_of_checked = dict()
            line_counter = 0
            for row_in_new in new_data:
                line_counter += 1
                count_in = 0  # счетчик совпадений в текущей бд
                for row_in_cur in cur_data:
                    if str(row_in_new[0]) == str(row_in_cur[0]):  # если нашлась в текуще бд запись с таким же id
                        count_in += 1  # нашли совпадение - увеличили счетчик
                        count = 0  # счетчик изменений в строк
                        if row_in_new[0] in map_of_checked:
                            if self.showDilemaBox("Совпадение", "Запись с id = " + str(row_in_new[0]) +
                                                                " уже была обработана в строке номер "
                                                                + str(map_of_checked[row_in_new[0]]) +
                                                                " в ходе обновления\n"
                                                                "Вы хотите обновить запись еще раз?\n"
                                                                "Если нет -  данные в строке " + str(line_counter) +
                                                                " не сохраняться") == 1:
                                print("Запись будет обновлена")
                            else:
                                print("Обновление приостановлено")
                                continue
                        for iterator in range(1, len(list_result_headers)):  # пробегаемся по всем колонам, кроме первой
                            if row_in_new[iterator] != str(row_in_cur[iterator]):  # если есть несовпадение
                                count += 1  # увеличиваем счетчик изменений
                                # формируем UPDATE запрос
                                header = str(list_result_headers[iterator])
                                query = "UPDATE " + table + " SET " + header + " = ? WHERE " + table[0:-1] + \
                                        "_id = " + str(row_in_new[0]) + ";"
                                if type(row_in_new[iterator]) is int:
                                    data = int(row_in_new[iterator])
                                else:
                                    data = str(row_in_new[iterator])
                                try:
                                    print(query, data)
                                    self.conn.execute(query, (data,))
                                    self.conn.commit()
                                    error = None
                                except Exception as exc:
                                    error = str(exc)
                                if error is not None:
                                    if error == "UNIQUE constraint failed: " + table + table[0:-1] + \
                                            "_id":
                                        print("insert_" + error)
                                    else:
                                        self.showMessageBox("Внимание!", "Произошла ошибка при обновлении: " + error,
                                                            'error')
                                else:
                                    print("Изменение успешно сохранено")
                        if count != 0:  # если в строке есть изменение, то извещаем пользователя
                            self.showMessageBox("Обновление", "Изменения строки c полем '" +
                                                table[0:-1] + "_id', которое равно " +
                                                row_in_new[0] + " успешно внесены в базу данных", 'info')
                            map_of_checked[row_in_new[0]] = line_counter
                        elif count == 0:  # если изменений нет, то ничего не делаем
                            map_of_checked[row_in_new[0]] = line_counter
                            print("Внимание! Запись с полем '" + table[0:-1] + "_id', которое равно "
                                  + row_in_new[0] + " уже существует и не нуждается в обновлении")
                            continue  # переходим к следущей строке new_data

                if count_in == 0:  # если совпадений нет, то данную строку надо добавить в бд
                    query = "INSERT INTO " + table + " VALUES("
                    data = []
                    for item in row_in_new:
                        data.append(item)
                        query += "?,"
                    query = query[0:-1]
                    query += ")"
                    try:
                        print(query, data)
                        self.conn.execute(query, data)
                        self.conn.commit()
                        error = None
                    except Exception as exc:
                        error = str(exc)
                    if error is not None:
                        if error == "UNIQUE constraint failed: " + table + table[0:-1] + "_id":
                            print("count_in_" + error)
                        else:
                            self.showMessageBox("Внимание!", "Произошла ошибка при добавлении: " + error, 'error')
                    else:
                        map_of_checked[row_in_new[0]] = line_counter
                        self.showMessageBox("Обновление", "Строка c полем '" +
                                            table[0:-1] + "_id', которое равно " +
                                            row_in_new[0] + " успешно добавлена в базу данных", 'info')

            # теперь проверяем на удаление строк
            for row_in_cur in cur_data:  # сравниваем строку в текущей бд
                count_out = 0  # счетчик совпадений в текущей бд
                for row_in_new in new_data:  # со строками в новой бд // нашей таблице
                    if str(row_in_new[0]) == str(row_in_cur[0]):  # если нашлась в новой бд запись с таким же id
                        count_out += 1  # увеличиваем счетчик
                if count_out == 0:  # если счетчик не увеличился, значит совпадений нет
                    # Формируем запрос на удаление
                    data_id = str(row_in_cur[0])
                    query = "DELETE FROM " + table + " WHERE " + table[0:-1] + "_id = :data_id;"
                    try:
                        print("DELETE FROM " + table + " WHERE " + table[0:-1] + "_id = " + data_id)
                        self.conn.execute(query, {"data_id": data_id})
                        self.conn.commit()
                        error = None
                    except Exception as exc:
                        error = str(exc)
                    if error is not None:
                        if error == "UNIQUE constraint failed: " + table + table[0:-1] + "_id":
                            print("count_in_" + error)
                        else:
                            self.showMessageBox("Внимание!", "Произошла ошибка при удалении: " + error, 'error')
                    else:
                        self.showMessageBox("Удаление", "Строка c полем '" +
                                            table[0:-1] + "_id', которое равно " +
                                            str(row_in_cur[0]) + " успешно удалена из базы данных", 'info')
        else:
            self.add_column(table, new_cols)
            self.update_date(table, new_data, new_columns_names)
            print("Херачь новый метод")

    def add_column(self, table, new_columns):
        for item in new_columns:
            query = "ALTER TABLE " + table + " ADD COLUMN " + item
            print(query)
            self.conn.execute(query)
            self.conn.commit()

    def showMessageBox(self, title, message, case):
        msg_box = QMessageBox()
        if case == "error":
            msg_box.setIcon(QMessageBox.Warning)
        elif case == 'info':
            msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()

    def showDilemaBox(self, title, message):
        dil_box = QMessageBox()
        dil_box.setIcon(QMessageBox.Question)
        dil_box.setWindowTitle(title)
        dil_box.setText(message)
        dil_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        if dil_box.exec() == QMessageBox.Yes:
            return 1
        else:
            return 0

    def __del__(self):
        if self.dbname != "":
            self.conn.close()


class DBFormWindow(QMainWindow):
    def __init__(self, user_id, parent=None):
        QMainWindow.__init__(self, parent)

        self.user = user_id
        print("Current user_id: " + self.user)

        self.setMinimumSize(QSize(640, 480))  # Устанавливаем размеры
        self.setWindowTitle("Работа БД")  # Устанавл заголовок окна
        self.central_widget = QWidget(self)  # Создаём центральный виджет
        self.setCentralWidget(self.central_widget)  # Устанавливаем центральный виджет

        self.verticalLayoutWidget = QtWidgets.QWidget(self.central_widget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 10, 600, 90))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QHBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")

        self.horizontalLayoutWidget1 = QtWidgets.QWidget(self.verticalLayoutWidget)
        self.horizontalLayoutWidget1.setGeometry(QtCore.QRect(10, 0, 589, 30))
        self.horizontalLayoutWidget1.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout1 = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget1)
        self.horizontalLayout1.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout1.setObjectName("horizontalLayout")

        self.db_path = ""
        self.loginDatabase = LoginDatabase('')  # Соединяемся с бд

        self.select_db = QComboBox(self)
        self.horizontalLayout1.addWidget(self.select_db)

        self.fill_select_db()
        self.select_db.activated[str].connect(self.open_db)

        self.select_table = QComboBox(self)
        self.horizontalLayout1.addWidget(self.select_table)
        self.select_table.insertItem(0, "--Выберите таблицу--")
        self.select_table.activated[str].connect(self.open_table)

        add_button = QPushButton("Добавить пустую строку", self)  # добавляет строку ниже
        self.verticalLayout.addWidget(add_button)

        if self.user == '0':
            add_column_button = QPushButton("Добавить столбец", self)  # добавляет строку ниже
            self.horizontalLayout1.addWidget(add_column_button)
            add_column_button.clicked.connect(self.add_column)

        update_button = QPushButton("Обновить базу данных", self)
        self.verticalLayout.addWidget(update_button)

        self.select_sort = QComboBox(self)
        self.verticalLayout.addWidget(self.select_sort)
        self.select_sort.insertItem(0, "Сортировать по...")

        self.table = QTableWidget(self)
        self.table.setGeometry(QtCore.QRect(10, 80, 610, 380))

        add_button.clicked.connect(self.add_string)
        update_button.clicked.connect(self.update_data)

    def add_column(self):
        try:
            if self.select_table.currentIndex() == 0:
                LoginDatabase.showMessageBox(self.loginDatabase, "Внимание", 'Сначала необходимо выбрать ' +
                                             'базу данных и таблицу', 'info')
            else:
                print('adding empty column')
                # print(self.select_table.currentIndex())
                print("old col count = " + str(self.table.columnCount()))
                self.table.setColumnCount(self.table.columnCount() + 1)
                print("new col count = " + str(self.table.columnCount()))
        except Exception as er:
            error = str(er)
            print(error)

    def fill_select_db(self):
        self.select_db.insertItem(0, "--Выберите базу данных--")
        data_bases = [f for f in listdir(os.path.abspath(os.curdir)) if isfile(join(os.path.abspath(os.curdir), f))
                      and f[-5:len(f)] == ".s3db"]
        counter = 1
        for DB in data_bases:
            self.select_db.insertItem(counter, DB)
            counter += 1

    def open_db(self):
        if self.select_db.currentIndex() == 0:
            if self.table.rowCount() != 0:
                if LoginDatabase.showDilemaBox(LoginDatabase, "Внимание", "Обновить текущую таблицу перед ее закрытием "
                                                                          "?") == 1:
                    self.update_data()
            self.table.clear()
            self.table.setRowCount(0)
            self.select_table.clear()
            self.select_table.insertItem(0, "--Выберите таблицу--")
            self.select_table.setCurrentIndex(0)
            print("База Данных не выбрана")
        else:
            if self.table.rowCount() != 0:
                if LoginDatabase.showDilemaBox(LoginDatabase, "Внимание", "Обновить текущую таблицу перед ее закрытием "
                                                                          "?") == 1:
                    self.update_data()
            self.table.clear()
            self.table.setRowCount(0)
            self.select_table.clear()
            self.select_table.insertItem(0, "--Выберите таблицу--")
            self.select_table.setCurrentIndex(0)
            self.db_path = self.select_db.currentText()
            print(self.db_path)
            self.loginDatabase = LoginDatabase(self.db_path)
            print(self.loginDatabase)
            self.fill_selected_tables()

    def fill_selected_tables(self):
        self.select_table.clear()
        self.select_table.insertItem(0, "--Выберите таблицу--")
        if self.select_db.currentIndex() != 0:
            print("Заполнение таблицы Базы Данных: " + str(self.loginDatabase.table_names))
            counter = 0
            for column_description in self.loginDatabase.table_names:
                counter += 1
                self.select_table.insertItem(counter, column_description)

    def open_table(self):
        if self.select_table.currentIndex() == 0:
            print("Значение сортировки не выбрано")
            return "nothing"
        else:
            self.select_sort.clear()
            self.select_sort.insertItem(0, "Сортировать по...")
            names = self.loginDatabase.tables_names(self.select_table.currentText())
            counter = 0
            for column_description in names:
                counter += 1
                self.select_sort.insertItem(counter, column_description[0])
            self.select_sort.activated[str].connect(self.sort_by)

            self.print_table()
            return self.select_table.currentText()

    def print_table(self):

        count_str = self.loginDatabase.count_strings(self.select_table.currentText())
        names_tables = self.loginDatabase.tables_names(self.select_table.currentText())
        sort_mode = self.sort_by()
        # print(sort_mode)
        self.table.setColumnCount(len(names_tables))  # Устанавливаем колонки
        self.table.setRowCount(count_str)  # и строки в таблице

        # Получаем список колон
        result_headers = ""
        for column_description in names_tables:
            result_headers += column_description[0] + " "
        list_result_headers = result_headers[0:(len(result_headers) - 1)].split(" ")
        # print(list_result_headers)
        # Устанавливаем заголовки таблицы
        self.table.setHorizontalHeaderLabels(list_result_headers)

        select_result = ""
        if sort_mode == "nothing":
            # print('without mode')
            select_result = self.loginDatabase.show_date(self.select_table.currentText())
        else:
            # print("With mode")
            select_result = self.loginDatabase.sort(self.select_table.currentText(), sort_mode)

        # print(select_result)

        # заполняем строки
        for counter, value in enumerate(select_result):
            for j in range(len(value)):
                data = str(value[j])
                self.table.setItem(counter, j, QTableWidgetItem(data))

    def add_string(self):
        try:
            if self.select_table.currentIndex() == 0:
                LoginDatabase.showMessageBox(self.loginDatabase, "Внимание", 'Сначала необходимо выбрать ' +
                                             'базу данных и таблицу', 'info')
            else:
                print('adding empty line')
                self.table.setRowCount(self.table.rowCount() + 1)
        except Exception as er:
            error = str(er)
            print(error)
            LoginDatabase.showMessageBox(self.loginDatabase, "Внимание", 'Сначала необходимо выбрать ' +
                                         'базу данных и таблицу', 'info')

    def update_data(self):  # обновление базы данных. Проверка на пустоту и запрос на обновлении
        try:
            if self.select_db.currentIndex() == 0:
                LoginDatabase.showMessageBox(self.loginDatabase, "Внимание", 'Сначала необходимо выбрать ' +
                                             'базу данных и таблицу', 'info')
            else:
                result_list = list("")
                for i in range(self.table.rowCount()):
                    result_text = ""
                    empty = 0
                    first_empty = self.table.columnCount()
                    for j in range(self.table.columnCount()):
                        if self.table.item(i, j) == None or self.table.item(i, j).text() == "":
                            if first_empty > j + 1:
                                first_empty = j + 1
                            empty = empty + 1
                        else:
                            result_text += self.table.item(i, j).text() + "_"
                    if empty == self.table.columnCount():  # если вся строка пустая
                        print("Пустая строка - " + str(i + 1) + " строка")
                    elif empty == 0:  # если вся строка фулл
                        pass
                    else:  # если в строке есть пустое поле
                        self.loginDatabase.showMessageBox("ОШИБКА", "Пустое поле в " + str(first_empty) + " столбце "
                                                          + str(i + 1) + " строки", 1)
                        return 1
                    if result_text == '':
                        pass
                    else:
                        result_list_j = list(result_text[0:(len(result_text) - 1)].split("_"))
                        result_list.append(result_list_j)
                print(result_list)
                list_tables = []
                col = len(self.loginDatabase.tables_names(self.select_table.currentText()))
                if col == len(result_list[0]):
                    self.loginDatabase.update_date(self.select_table.currentText(), result_list, [])
                elif col < len(result_list[0]):
                    for i in range(len(result_list[0]) -
                                   len(self.loginDatabase.tables_names(self.select_table.currentText()))):
                        new_table_name = self.set_new_table_name("Добавление нового столбца",
                                                                 'Введите название нового столбца:')
                        list_tables.append(new_table_name)
                    print(list_tables)
                    self.loginDatabase.update_date(self.select_table.currentText(), result_list, list_tables)
                self.print_table()
        except Exception as er:
            error = str(er)
            print(error)

    def set_new_table_name(self, title, message):
        text, ok = QInputDialog.getText(self, title, message, QLineEdit.Normal, "")
        if ok:
            return text

    def sort_by(self):
        curr_txt = self.select_sort.currentText()
        if self.select_sort.currentIndex() == 0:
            print("Значение сортировки не выбрано")
            return "nothing"
        else:
            return curr_txt

    def closeEvent(self, e):
        result = LoginDatabase.showDilemaBox(self.loginDatabase, "Выход", "Вы уверены, что хотите выйти?")
        if result == 1:
            e.accept()
        else:
            e.ignore()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = DBFormWindow('0')
    w.show()
    # ex = Dialog()
    sys.exit(app.exec_())
