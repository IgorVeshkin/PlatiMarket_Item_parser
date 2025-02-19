# Данный файл предназначен для удаление записи из базы данных

# Импорт для проверки наличия файла базы данных
import os

from DatabaseOperation.databaseBasicOperations import createDatabase, buildSqlConnection, closeSqlConnection

from DatabaseOperation.databaseInteractionOperations import deleteRecord


def main():

    # Название и/или путь до файла базы данных
    my_database_path = 'PlatiMarket_db.db'

    # Если база данных по указанному пути не найдена
    if not os.path.isfile(my_database_path):
        # Создаю базу данных определенной структуры
        sql_connection, sql_cursor = createDatabase(db_name=my_database_path)

        print(
            'Поскольку база была только что создана, данных для удаления в ней быть не может. Инициирован выход из программы...')
        return
    else:
        # Если база существует, просто формируем подключение
        sql_connection, sql_cursor = buildSqlConnection(db_name=my_database_path)


    print('Запущен скрипт удаления записи из базы данных...\n')

    # Получаю id данных из таблицы Item_Data для удаления
    data_id = input('Введите id записи из таблицы Item_Data: ')

    # Удаляю запись из таблицы Item_Data
    deleteRecord(sql_connection, sql_cursor, data_uuid=data_id)

    # Закрываю соединение
    closeSqlConnection(sqlite_connection=sql_connection)


if __name__=='__main__':
    main()
