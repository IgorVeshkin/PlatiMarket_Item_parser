# Данный скрипт предназначен для вывода общих данных товара и данных обновляемой части (цен, продаж, возвратов)
# без запуска парсера в скрипте PlatiMarket_Update_Items.py

# Импорт для проверки наличия файла базы данных
import os

# Импорт функции создания базы данных, построения связи и закрытия связи. Своя функция
from DatabaseOperation.databaseBasicOperations import createDatabase, buildSqlConnection, closeSqlConnection

# Импорт функции проверки наличия записи в базе и создания записи базы данных. Своя функция
from DatabaseOperation.databaseInteractionOperations import getRecordUpdatableData, getAllProductUrls


def main():
    # Название и/или путь до файла базы данных
    my_database_path = 'PlatiMarket_db.db'

    # Если база данных по указанному пути не найдена
    if not os.path.isfile(my_database_path):
        # Создаю базу данных определенной структуры
        sql_connection, sql_cursor = createDatabase(db_name=my_database_path)

        print('Поскольку база была только что создана, данных для автоматического обновления парсинга в ней быть не может. Инициирован выход из программы...')
        return
    else:
        # Если база существует, просто формируем подключение
        sql_connection, sql_cursor = buildSqlConnection(db_name=my_database_path)

    # getAllProductUrls возвращает связку id_товара и ссылка_товара,
    # ссылки мне не нужны, но поскольку функция возвращает id, то использую ее
    data_uuids, data_urls = getAllProductUrls(sql_cursor)

    # Выполняю вывод через цикл
    for data_uuid in data_uuids:
        # Вывод данных
        getRecordUpdatableData(sql_cursor, data_uuid)

    # Закрываю соединение с базой данных
    closeSqlConnection(sqlite_connection=sql_connection)


if __name__=='__main__':
    main()
