import sqlite3 as db
from PyQt5.Qt import *

DB_PATH = "fin_bd.s3db"
table_name = "sessions"


class LoginDatabase():
    def __init__(self, dbname):
        self.dbname = DB_PATH
        self.conn = db.connect(dbname)

    def tables_names(self):  # выводит наименование столбцов
        query = "SELECT * FROM " + table_name + ";"
        cursor = self.conn.execute(query)
        result = cursor.description
        # print(result)
        return result

    def select_all_query(self):  # выводит всю бд
        query = "SELECT * FROM " + table_name + ";"
        cursor = self.conn.execute(query)
        result = cursor.fetchall()
        # print(result)
        return result

    def count_strings(self):  # выводит количество записей // строк
        query = "SELECT COUNT(*) FROM " + table_name + ";"
        cursor = self.conn.execute(query)
        result = cursor.fetchone()
        # print(result[0])
        return result[0]

    def show_date(self):  # выводит всю таблицу
        query = "SELECT * FROM " + table_name + ";"
        cursor = self.conn.execute(query)
        result = cursor.fetchall()
        # print(result)
        return result

    def update_date(self, new_data):  # обнавляет таблицу
        cur_data = self.select_all_query()
        columns_name = self.tables_names()
        # print(columns_name)
        # Получаем список колон
        result_headers = ""
        for column_description in columns_name:
            result_headers += column_description[0] + " "
        list_result_headers = result_headers[0:(len(result_headers) - 1)].split(" ")
        # print(list_result_headers)
        # print(new_data)
        for row_in_new in new_data:
            count_in = 0  # счетчик совпадений в текущей бд
            for row_in_cur in cur_data:
                if str(row_in_new[0]) == str(row_in_cur[0]):  # если нашлась в текуще бд запись с таким же id
                    count_in += 1  # нашли совпадение - увеличили счетчик
                    count = 0  # счетчик изменений в строке
                    for iterator in range(1, len(list_result_headers) - 1):  # пробегаемся по всем колонам, кроме первой
                        if row_in_new[iterator] != str(row_in_cur[iterator]):  # если есть несовпадение
                            count += 1  # увеличиваем счетчик изменений
                            # формируем UPDATE запрос
                            query = "UPDATE " + table_name + " SET " + str(list_result_headers[iterator]) + " = "
                            if type(row_in_cur[iterator]) == 'int':  # если инт
                                query += str(row_in_new[iterator])  # ковычки не нужны
                            else:
                                query += '"' + str(row_in_new[iterator]) + '"'  # иначе - ставим
                            query += " WHERE " + table_name[0:-1] + "_id = " + str(row_in_new[0]) + ";"
                            # print(query)
                            try:
                                print(query)
                                self.conn.execute(query)
                                self.conn.commit()
                                error = None
                            except Exception as exc:
                                error = str(exc)
                            # self.conn.close()
                            if error is not None:
                                if error == "UNIQUE constraint failed: students.student_id":
                                    print("insert_" + error)
                                else:
                                    self.showMessageBox("Внимание!", "Произошла ошибка: " + error)
                            else:
                                print("Изменение успешно сохранено")
                    if count != 0:  # если в строке есть изменение, то извещаем пользователя
                        self.showMessageBox("Обновление", "Изменения строки c полем '" +
                                            table_name[0:-1] + "_id', которое равно " +
                                            row_in_new[0] + " успешно внесены в базу данных")
                    elif count == 0:  # если изменений нет, то ничего не делаем
                        print("Внимание! Запись с полем '" + table_name[0:-1] + "_id', которое равно "
                              + row_in_new[0] + " уже существует и не нуждается в обновлении")
                        continue  # переходим к следущей строке new_data
            if count_in == 0:  # если совпадений нет, то данную строку надо добавить в бд
                query = "INSERT INTO " + table_name + " VALUES("
                for item in row_in_new:
                    if type(item) == "int":
                        query += item + ", "
                    else:
                        query += "'" + item + "', "
                query = query[0:-2]
                query += ")"
                try:
                    print(query)
                    cursor = self.conn.execute(query)
                    self.conn.commit()
                    error = None
                except Exception as exc:
                    error = str(exc)
                if error is not None:
                    if error == "UNIQUE constraint failed: students.student_id":
                        print("count_in_" + error)
                    else:
                        self.showMessageBox("Внимание!", "Произошла ошибка: " + error)
                else:
                    self.showMessageBox("Обновление", "Строка c полем '" +
                                        table_name[0:-1] + "_id', которое равно " +
                                        row_in_new[0] + " успешно добавлена в базу данных")

        # теперь проверяем на удаление строк
        for row_in_cur in cur_data:  # сравниваем строку в текущей бд
            count_out = 0  # счетчик совпадений в текущей бд
            for row_in_new in new_data:  # со строками в новой бд // нашей таблице
                if str(row_in_new[0]) == str(row_in_cur[0]):  # если нашлась в новой бд запись с таким же id
                    count_out += 1  # увеличиваем счетчик
            if count_out == 0:  # если счетчик не увеличился, значит совпадений нет
                # Формируем запрос на удаление
                query = "DELETE FROM " + table_name + " WHERE " + table_name[0:-1] + "_id = " + str(row_in_cur[0]) + ";"
                try:
                    print(query)
                    self.conn.execute(query)
                    self.conn.commit()
                    error = None
                except Exception as exc:
                    error = str(exc)
                if error is not None:
                    if error == "UNIQUE constraint failed: students.student_id":
                        print("count_in_" + error)
                    else:
                        self.showMessageBox("Внимание!", "Произошла ошибка: " + error)
                else:
                    self.showMessageBox("Удаление", "Строка c полем '" +
                                        table_name[0:-1] + "_id', которое равно " +
                                        str(row_in_cur[0]) + " успешно удалена из базы данных")

    def showMessageBox(self, title, message):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()

    def __del__(self):
        self.conn.close()


# Наследуемся от QMainWindow
class SessionsWindow(QMainWindow):
    additional_strings_count = 0  # количество строк добавленное во время одной сессии

    # Переопределяем конструктор класса
    def __init__(self):
        # Обязательно нужно вызвать метод супер класса
        QMainWindow.__init__(self)

        self.setMinimumSize(QSize(880, 480))  # Устанавливаем размеры
        self.setWindowTitle("Работа с таблицей " + table_name)  # Устанавливаем заголовок окна
        central_widget = QWidget(self)  # Создаём центральный виджет
        self.setCentralWidget(central_widget)  # Устанавливаем центральный виджет

        grid_layout = QGridLayout()  # Создаём QGridLayout
        central_widget.setLayout(grid_layout)  # Устанавливаем данное размещение в центральный виджет

        # Соединяемся с бд
        self.loginDatabase = LoginDatabase(DB_PATH)
        self.table = QTableWidget(self)  # Создаём таблицу
        self.print_table(self.table)

        add_button = QPushButton("Добавить пустую строку", self) # добавляет строку ниже
        add_button.clicked.connect(self.add_string)

        update_button = QPushButton("Обновить базу данных", self)
        update_button.clicked.connect(self.update_data)

        delete_empty_button = QPushButton("Удалить пустые строки (Необходимое действие перед обновлением базы"
                                          " данных)", self)
        delete_empty_button.clicked.connect(self.delete_empty)

        grid_layout.addWidget(self.table, 0, 0)  # Добавляем таблицу в сетку
        grid_layout.addWidget(add_button, 1, 0)  # Добавляем кнопку в сетку
        grid_layout.addWidget(update_button, 2, 0)
        grid_layout.addWidget(delete_empty_button, 3, 0)

    def print_table(self, table):
        count_str = self.loginDatabase.count_strings() + SessionsWindow.additional_strings_count
        names_tables = self.loginDatabase.tables_names()

        table.setColumnCount(len(names_tables))  # Устанавливаем колонки
        table.setRowCount(count_str)  # и строки в таблице

        # Получаем список колон
        result_headers = ""
        for column_description in names_tables:
            result_headers += column_description[0] + " "
        list_result_headers = result_headers[0:(len(result_headers) - 1)].split(" ")
        # Устанавливаем заголовки таблицы
        table.setHorizontalHeaderLabels(list_result_headers)

        # попробовать закинуть в отдельный метод
        select_result = self.loginDatabase.show_date()
        # print(select_result)
        # print(StreamsWindow.additional_strings_count)
        # заполняем строки
        for counter, value in enumerate(select_result):
            # print("value = " + str(value))
            # print("counter = " + str(counter))
            for j in range(len(value) + SessionsWindow.additional_strings_count):
                # print("j = " + str(j))
                if j >= len(value):
                    data = ""
                else:
                    data = str(value[j])
                table.setItem(counter, j, QTableWidgetItem(data))

        # нужен костыль, который отрисовывает последнюю строку, или норм решение

        # тут идет костыль (надо бы нормально найти причину опустошения последнего столбца, но сроки горят)
        for counter, value in enumerate(select_result):
            # print(value[table.columnCount() - 1])
            table.setItem(counter, self.table.columnCount() - 1, QTableWidgetItem(str(value[self.table.columnCount() - 1])))

    def add_string(self):
        new_count = SessionsWindow.additional_strings_count + 1
        SessionsWindow.additional_strings_count = new_count
        self.bdWindow = SessionsWindow()
        self.bdWindow.show()
        self.close()

    def update_data(self):  # обновление базы данных
        result_list = list("")
        for i in range(self.table.rowCount()):
            result_text = ""
            for j in range(self.table.columnCount()):
                if self.table.item(i, j) == None or self.table.item(i, j).text() == "":
                    self.showMessageBox("ОШИБКА", "Пустое поле в " + str(j+1) + " столбце " +
                                        str(i+1) + " строки")
                    return
                else:
                    result_text += self.table.item(i, j).text() + "_"
                # print(self.table.item(i, j).text())
            result_list_j = list(result_text[0:(len(result_text) - 1)].split("_"))
            result_list.append(result_list_j)

        self.additional_strings_count = 0
        # print(result_list)
        self.loginDatabase.update_date(result_list)
        self.bdWindow = SessionsWindow()
        self.bdWindow.show()
        self.close()

    def delete_empty(self):
        list_of_last_column = []
        empty_count = 0
        for i in range(self.table.rowCount()):
            empty_blocks_count = 0
            # print(self.table.rowCount())
            for j in range(self.table.columnCount()):
                if self.table.item(i, j) == None or self.table.item(i, j).text() == "":
                    empty_blocks_count += 1
                    # print("ОШИБКА! Одно из полей не заполнено")
                else:
                    list_of_last_column.append(self.table.item(i, j).text())
            if empty_blocks_count == self.table.columnCount():
                empty_count += 1
                print("Пустая строка - " + str(i+1) + " строка")
        print("Всего пустых строк " + str(empty_count))
        new_count = SessionsWindow.additional_strings_count - empty_count
        SessionsWindow.additional_strings_count = new_count

        self.bdWindow = StreamsWindow()
        self.bdWindow.show()
        self.close()

    def showMessageBox(self, title, message):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    mw = SessionsWindow()
    mw.show()
    sys.exit(app.exec())
