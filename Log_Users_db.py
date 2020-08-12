from PyQt5.Qt import *
import sqlite3 as db


class UsersDatabase():
    def __init__(self):
        self.conn = db.connect("data.s3db")

    def get_rights(self, table_name, user_id):
        query = "SELECT " + table_name + "_rights FROM data WHERE dat_id = " + str(user_id)
        print(query)
        try:
            cursor = self.conn.execute(query)
            result = cursor.fetchone()
        except Exception as error:
            print("Ошибка при запросе права доступа к таблице " + table_name + '_rights: ' + str(type(error)) + ": "
                  + str(error))
            expected_error = 'no such column: ' + table_name + '_rights'
            if str(error) == expected_error:
                print("Задание права по умолчанию")
                result = 'w'
            else:
                print("Непредвиденная ошибка")
                result = '-'
        print(result)
        return result

    def __del__(self):
        self.conn.close()


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
