import sqlite3 as db
from PyQt5.Qt import *

DB_PATH = "fin_bd.s3db"
# table_name = "sessions"
table_names = ["departments", "exams", 'sessions', 'streams', 'students']

class LoginDatabase():
    def __init__(self, dbname, num_of_table_in_names):
        self.dbname = DB_PATH
        self.conn = db.connect(dbname)
        self.table_name = table_names[num_of_table_in_names]

    def tables_names(self):  # выводит наименование столбцов
        query = "SELECT * FROM " + self.table_name + ";"
        cursor = self.conn.execute(query)
        result = cursor.description
        return result

    def select_all_query(self):  # выводит всю бд
        query = "SELECT * FROM " + self.table_name + ";"
        cursor = self.conn.execute(query)
        result = cursor.fetchall()
        return result

    def count_strings(self):  # выводит количество записей // строк
        query = "SELECT COUNT(*) FROM " + self.table_name + ";"
        cursor = self.conn.execute(query)
        result = cursor.fetchone()
        return result[0]

    def show_date(self):  # выводит всю таблицу
        query = "SELECT * FROM " + self.table_name + ";"
        cursor = self.conn.execute(query)
        result = cursor.fetchall()
        return result

    def sort(self, column_name):  # опытка сортировки
        query = "SELECT * FROM " + self.table_name + " ORDER BY ?"
        try:
            cursor = self.conn.execute(query, 'exam_amount')
            result = cursor.fetchall()
            self.conn.commit()
        except Exception as error:
            print(error)
        print(query, column_name)
        return result

    def update_date(self, new_data):  # обновляет таблицу
        cur_data = self.select_all_query()
        columns_name = self.tables_names()
        # Получаем список колон
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
                            query = "UPDATE sessions SET " + header + " = ? WHERE " + self.table_name[0:-1] + "_id = " + \
                                    str(row_in_new[0]) + ";"
                            try:
                                data = int(row_in_new[iterator])
                            except Exception as exc:
                                # print(exc)
                                data = str(row_in_new[iterator])
                            try:
                                print(query, data)
                                self.conn.execute(query, (data,))
                                self.conn.commit()
                                error = None
                            except Exception as exc:
                                error = str(exc)
                            if error is not None:
                                if error == "UNIQUE constraint failed: " + self.table_name + self.table_name[0:-1] + \
                                        "_id":
                                    print("insert_" + error)
                                else:
                                    self.showMessageBox("Внимание!", "Произошла ошибка при обновлении: " + error,
                                                        'error')
                            else:
                                print("Изменение успешно сохранено")

                    if count != 0:  # если в строке есть изменение, то извещаем пользователя
                        self.showMessageBox("Обновление", "Изменения строки c полем '" +
                                            self.table_name[0:-1] + "_id', которое равно " +
                                            row_in_new[0] + " успешно внесены в базу данных", 'info')
                        map_of_checked[row_in_new[0]] = line_counter
                    elif count == 0:  # если изменений нет, то ничего не делаем
                        map_of_checked[row_in_new[0]] = line_counter
                        print("Внимание! Запись с полем '" + self.table_name[0:-1] + "_id', которое равно "
                              + row_in_new[0] + " уже существует и не нуждается в обновлении")
                        continue  # переходим к следущей строке new_data

            if count_in == 0:  # если совпадений нет, то данную строку надо добавить в бд
                query = "INSERT INTO " + self.table_name + " VALUES("
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
                    if error == "UNIQUE constraint failed: " + self.table_name + self.table_name[0:-1] + "_id":
                        print("count_in_" + error)
                    else:
                        self.showMessageBox("Внимание!", "Произошла ошибка при добавлении: " + error, 'error')
                else:
                    map_of_checked[row_in_new[0]] = line_counter
                    self.showMessageBox("Обновление", "Строка c полем '" +
                                        self.table_name[0:-1] + "_id', которое равно " +
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
                query = "DELETE FROM " + self.table_name + " WHERE " + self.table_name[0:-1] + "_id = :data_id;"
                try:
                    print("DELETE FROM " + self.table_name + " WHERE " + self.table_name[0:-1] + "_id = " + data_id)
                    self.conn.execute(query, {"data_id": data_id})
                    self.conn.commit()
                    error = None
                except Exception as exc:
                    error = str(exc)
                if error is not None:
                    if error == "UNIQUE constraint failed: " + self.table_name + self.table_name[0:-1] + "_id":
                        print("count_in_" + error)
                    else:
                        self.showMessageBox("Внимание!", "Произошла ошибка при удалении: " + error, 'error')
                else:
                    self.showMessageBox("Удаление", "Строка c полем '" +
                                        self.table_name[0:-1] + "_id', которое равно " +
                                        str(row_in_cur[0]) + " успешно удалена из базы данных", 'info')

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
        dilema_box = QMessageBox()
        dilema_box.setIcon(QMessageBox.Question)
        dilema_box.setWindowTitle(title)
        dilema_box.setText(message)
        dilema_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        if dilema_box.exec() == QMessageBox.Yes:
            return 1
        else:
            return 0

    def __del__(self):
        self.conn.close()


# Наследуемся от QMainWindow
class TableWindow(QMainWindow):
    # Переопределяем конструктор класса
    def __init__(self, num_of_table_in_names):
        self.num_of_table_in_names = num_of_table_in_names  # индекс таблицы в table_names
        self.loginDatabase = LoginDatabase(DB_PATH, num_of_table_in_names)  # Соединяемся с бд
        # Обязательно нужно вызвать метод супер класса
        QMainWindow.__init__(self)

        self.setMinimumSize(QSize(880, 480))  # Устанавливаем размеры
        self.setWindowTitle("Работа с таблицей " + table_names[self.num_of_table_in_names])  # Устанавл заголовок окна
        central_widget = QWidget(self)  # Создаём центральный виджет
        self.setCentralWidget(central_widget)  # Устанавливаем центральный виджет

        grid_layout = QGridLayout()  # Создаём QGridLayout
        central_widget.setLayout(grid_layout)  # Устанавливаем данное размещение в центральный виджет

        self.table = QTableWidget(self)  # Создаём таблицу
        self.print_table()

        names_tables = self.loginDatabase.tables_names()
        counter = 0
        self.selected = QComboBox(self)
        self.selected.insertItem(counter, "Сортировать по...")
        for column_description in names_tables:
            counter += 1
            self.selected.insertItem(counter, column_description[0])
        self.selected.activated[str].connect(self.sort_by)

        add_button = QPushButton("Добавить пустую строку", self) # добавляет строку ниже
        add_button.clicked.connect(self.add_string)

        update_button = QPushButton("Обновить базу данных", self)
        update_button.clicked.connect(self.update_data)

        '''grid_layout.addWidget(self.table, 0, 0, 0, 0)  # Добавляем таблицу в сетку
        grid_layout.addWidget(add_button, 1, 0, 1, 1)  # Добавляем кнопку в сетку
        grid_layout.addWidget(update_button, 1, 1, 1, 1)'''

        grid_layout.addWidget(self.table, 0, 0)  # Добавляем таблицу в сетку
        grid_layout.addWidget(add_button, 1, 0)  # Добавляем кнопку в сетку
        grid_layout.addWidget(update_button, 2, 0)
        grid_layout.addWidget(self.select_  , 3, 0)

    def print_table(self):
        count_str = self.loginDatabase.count_strings()
        names_tables = self.loginDatabase.tables_names()
        sort_mode = self.sort_by()

        self.table.setColumnCount(len(names_tables))  # Устанавливаем колонки
        self.table.setRowCount(count_str)  # и строки в таблице

        # Получаем список колон
        result_headers = ""
        for column_description in names_tables:
            result_headers += column_description[0] + " "
        list_result_headers = result_headers[0:(len(result_headers) - 1)].split(" ")
        # Устанавливаем заголовки таблицы
        self.table.setHorizontalHeaderLabels(list_result_headers)

        # попробовать закинуть в отдельный метод
        select_result = ""
        if sort_mode == "nothing":
            select_result = self.loginDatabase.show_date()
        else:
            select_result = self.loginDatabase.sort(sort_mode)

        # заполняем строки
        for counter, value in enumerate(select_result):
            for j in range(len(value)):
                data = str(value[j])
                self.table.setItem(counter, j, QTableWidgetItem(data))

    def add_string(self):
        print('adding empty line')
        self.table.setRowCount(self.table.rowCount() + 1)
        for i in range(self.table.columnCount()):
            self.table.setItem(self.table.rowCount(), i, QTableWidgetItem(""))

    def update_data(self):  # обновление базы данных. Проверка на пустоту и запрос на обновление
        result_list = list("")
        for i in range(self.table.rowCount()):
            result_text = ""
            empty = 0
            first_empty = self.table.columnCount()
            for j in range(self.table.columnCount()):
                if self.table.item(i, j) == None or self.table.item(i, j).text() == "":
                    if first_empty > j + 1 :
                        first_empty = j + 1
                    empty = empty + 1
                else:
                    result_text += self.table.item(i, j).text() + "_"
            if empty == self.table.columnCount(): # если вся строка пустая
                print("Пустая строка - " + str(i+1) + " строка")
            elif empty == 0:  # если вся строка фулл
                pass
            else:  # если в строке есть пустое поле
                self.loginDatabase.showMessageBox("ОШИБКА", "Пустое поле в " + str(first_empty) + " столбце "
                                                  + str(i+1) + " строки", 1)
                return 1
            if result_text == '':
                pass
            else:
                result_list_j = list(result_text[0:(len(result_text) - 1)].split("_"))
                result_list.append(result_list_j)
        self.additional_strings_count = 0
        print(result_list)
        self.loginDatabase.update_date(result_list)
        self.print_table()

    def sort_by(self):
        curr_txt = self.selected.currentText()
        if self.selected.currentIndex() == 0:
            print("Значение сортировки не выбрано")
            return "nothing"
        else:
            return curr_txt

    def closeEvent(self, e):
        result = self.loginDatabase.showDilemaBox("Выход", "Вы уверены, что хотите выйти?")
        if result == 1:
            e.accept()
        else:
            e.ignore()


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    mw = TableWindow(2)
    mw.show()
    sys.exit(app.exec())
