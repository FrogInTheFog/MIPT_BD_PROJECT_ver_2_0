# MIPT_BD_PROJECT

DB project for 6 sem MIPT


Данные файлы являются проектом по базам данным 6 семеста МФТИ, который представляет из себя взаимодействие с базами данных с помощью некой графической оболочки

main.py - главный файл проекта, который осуществляет взаимодействия с базами данных

window_ver_2.ui - графическая оболочка данного проекта, написанная с помощью PyQt5

mybd2.s3db - тестовая база данных

mytest_bd_creat.py - вспомогательный файл, создающий тестовую базу данных, которая заполнена данными и была написана на парах

My_bd_creator.py - вспомогательныый файл, создающий базу данных, которую написал лично, но не заполнил (в каждой таблице по одному элементу)

fin_bd.s3db - моя база данных, которая создается файлом выше

При компиляция главного файла проекта появляется окно с некоторыми кнопками:
  - Select DB - выбирает базу данных, которая находится на данный момент на ПК. На данный момент позволяет только просматривать базы данных (select).
  - Select incode DB - выбирает базу данных, которая указана в файле main.py под именем DB_PATH (на данный момент это mybd2.s3db). Позволяет полностью взаимодействовать с базой данных (Insert/delete/select)
  - Enter - позволяет ввести команду, которая написана в поле ввода.
  
 Имеется 2 поля: 
  - поле вывода (большое поле) - История запросов и ответов на запросы. При двойном шелчке на предыдущий запрос, запрос вставляется в поле ввода
  - поле ввода (малое поле) - Поле для ввода SQL команд
  
 Для завершения работы программы необходимо закрыть окно. 
