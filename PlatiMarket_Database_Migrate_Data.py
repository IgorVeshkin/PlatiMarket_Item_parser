# Данный скрипт предназначен для переноса данных из PlatiMarket_db_Backup.db в PlatiMarket_db.db
# Подрзумивается, что файлы баз данных имеются


from DatabaseOperation.databaseBasicOperations import buildSqlConnection, closeSqlConnection


def main():
    print('Начинаю считывание данных из backup базы данных...')

    # Название и/или путь до файла базы данных backup
    my_database_path_backup = 'PlatiMarket_db_Backup.db'

    # Поскольку скрипт разрабатывается для переноса данных для одного случая,
    # нет смысла делать проверку на наличие баз данных

    # Построение соединения с базой данных backup-а
    sql_connection_backup, sql_cursor_backup = buildSqlConnection(db_name=my_database_path_backup)

    # Копирование данных из PlatiMarket_db_Backup.db

    # Выполняю sql-запрос на получение всех данных продавцов
    sql_cursor_backup.execute("""SELECT * FROM Seller""")

    # Получаю данные продавцов и заношу в переменную
    sellers_backup = sql_cursor_backup.fetchall()

    # Выполняю sql-запрос на получение всех данных таблицы Item_Data
    sql_cursor_backup.execute("""SELECT * FROM Item_Data""")

    # Получаю данные Item_Data и заношу в переменную
    item_data_backup = sql_cursor_backup.fetchall()

    # Выполняю sql-запрос на получение всех данных таблицы Item_Updatable_Data
    sql_cursor_backup.execute("""SELECT * FROM Item_Updatable_Data""")

    # Получаю данные Item_Updatable_Data и заношу в переменную
    item_updatable_data_backup = sql_cursor_backup.fetchall()

    # Выполняю sql-запрос на получение всех данных таблицы Item_Url
    sql_cursor_backup.execute("""SELECT * FROM Item_Url""")

    # Получаю данные Item_Url и заношу в переменную
    item_url_backup_data = sql_cursor_backup.fetchall()

    # Закрываю соединение с базой данных backup-а
    closeSqlConnection(sqlite_connection=sql_connection_backup)

    print('\nДанные успешно считаны с backup базы данных...\n')


    print('Начинаю передачу записей в новую базу данных...')

    # Путь до базы данных и ее название
    my_database_path = 'PlatiMarket_db.db'

    # Открываю соединение с базой данных, в которую будут перенесены данные из backup-а
    sql_connection, sql_cursor = buildSqlConnection(db_name=my_database_path)

    # Создаю записи в новой базе данных для таблицы Seller из данных backup-а
    # Переносятся даже даты создания и обновления записей
    sql_cursor.executemany(
        """INSERT INTO Seller (id, name, accountURL, creationDateTime, updatedDateTime) VALUES (?, ?, ?, ?, ?)""",
        sellers_backup)

    # Делаю коммит данных для добавления в базу данных
    sql_connection.commit()

    # Создаю записи в новой базе данных для таблицы Item_Data из данных backup-а
    # Переносятся даже даты создания и обновления записей
    sql_cursor.executemany(
        """INSERT INTO Item_Data (id, name, seller, ImageURL, creationDateTime, updatedDateTime) VALUES (?, ?, ?, ?, ?, ?)""",
        item_data_backup)

    # Делаю коммит данных для добавления в базу данных
    sql_connection.commit()

    # Создаю записи в новой базе данных для таблицы Item_Updatable_Data из данных backup-а
    # Переносятся даже дата создания
    sql_cursor.executemany(
        """INSERT INTO Item_Updatable_Data (id, price, soldCount, refundCount, ItemDataKey, creationDateTime) VALUES (?, ?, ?, ?, ?, ?)""",
        item_updatable_data_backup)

    # Делаю коммит данных для добавления в базу данных
    sql_connection.commit()

    # Создаю записи в новой базе данных для таблицы Item_Url из данных backup-а
    # Переносятся даже дата создания
    sql_cursor.executemany(
        """INSERT INTO Item_Url (id, url, data, creationDateTime) VALUES (?, ?, ?, ?)""",
        item_url_backup_data)

    # Делаю коммит данных для добавления в базу данных
    sql_connection.commit()

    # Закрываю соединение с базой данных
    closeSqlConnection(sqlite_connection=sql_connection)

    print('\nДанные успешно перенесены в новую базу данных...')

    # Внимание: Все перенеслось успешно, включая даты создания и обновления записей

    # Возможно, есть смысл сделать функционал backup-а базы данных


if __name__ =='__main__':
    main()