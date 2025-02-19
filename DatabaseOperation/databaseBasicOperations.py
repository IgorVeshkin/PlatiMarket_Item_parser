import sqlite3

def createDatabase(db_name: str ='database.db') -> tuple:
    """
        createDatabase: function

        Eng:
            creates new database of specific structure to store sellers and products data of PlatiMarket platform

        Rus:
            создает новую базу данных определенной структуры для хранения данных товаров и продавцов площадки PlatiMarket

        Args:
            db_name (str): name of database (or path)

        Returns:
            tuple:
                sqliteConnection (sqlite3.Connection): object to operate with current database connection
                cursor (sqlite3.Cursor): object to operate with database
    """

    print('База данных не была найдена...\n')
    print('Создаю новую базу данных необходимой структуры...\n')

    sqliteConnection = sqlite3.connect(db_name)

    cursor = sqliteConnection.cursor()

    # https://w3resource.com/sqlite/snippets/how-to-use-uuids-in-sqlite.php

    # Для самообновляющегося поля даты и времени updatedDateTime использую ON UPDATE CURRENT_TIMESTAMP,
    # чтобы внедрить данный функционал
    # Для создания поля использующего uuid тип вместо integer, достаточно просто указать тип UUID

    # ON UPDATE CURRENT_TIMESTAMP можно применить только в СУБД MySQL
    # CURRENT_TIMESTAMP можно заменить на (datetime('now','localtime'))
    cursor.execute("""
    CREATE TABLE Seller (
        id UUID PRIMARY KEY NOT NULL,
        name VARCHAR(255),            
        accountURL TEXT,
        creationDateTime TIMESTAMP DEFAULT (datetime('now','localtime')),
        updatedDateTime TIMESTAMP DEFAULT (datetime('now','localtime'))
        );""")

    # Создаю триггер для автоматического обновления updatedDateTime, вызываемое при обновлении записи
    # Обновленные данные updatedDataTime и изначальные creationDateTime не совпадают по формату

    # TODO: Updated at 26/01/2025: Починить Trigger по аналогии с триггером для Item_Data. Нужно ли вообще поле updatedDateTime для Seller?
    cursor.execute("""
    CREATE TRIGGER Seller_timestamp_update_Trigger
    AFTER UPDATE On Seller
    BEGIN
       UPDATE Seller SET updatedDateTime = STRFTIME('%Y-%m-%d %H:%M:%S', 'NOW', 'localtime') WHERE id = NEW.id;
    END;
        """)

    # FOREIGN KEY - это связь типа One-to-Many
    # У записи с информацией товара может быть только один продавец, тип связи One-to-One

    # Update at 25/12/2024: Доработка базы данных -> Добавляю ON DELETE CASCADE
    # По причине того, что делаю функционал удаления записи базы данных

    # ON DELETE CASCADE для seller означает, что если seller будет удален,
    # то и Item_Data запись, связанная с ним, тоже будет удалена

    cursor.execute("""
    CREATE TABLE Item_Data (
        id UUID PRIMARY KEY NOT NULL,
        name VARCHAR(255),
        seller UUID,
        ImageURL TEXT,
        creationDateTime TIMESTAMP DEFAULT (datetime('now','localtime')),
        updatedDateTime TIMESTAMP DEFAULT (datetime('now','localtime')),
        FOREIGN KEY(seller) REFERENCES Seller(id) ON DELETE CASCADE
        );""")

    # Update at 27/12/2024: Добавляю Trigger, чтобы сделать проверку: при удалении записи из таблицы Item_Data,
    # если у записи в Seller больше нет связанных записи в таблице Item_Data, то удаляю и из Seller

    # Update at 27/12/2024: TODO: Добавить триггер, удаляющий из Seller, если у продавца нет больше связанных записей в Item_Data, срабатываетпри удалении из Item_Data (Выполнено)

    # Условия в sqlite не поддерживаются

    # Триггер для автоматического удаления записи в таблице Seller

    # Тем не менее, данный триггер я закомментировать с помощью литерала, по причине использования на данный момент проверки на Python
    # Пусть будет proof-of-concept
    '''
    cursor.execute("""
        CREATE TRIGGER Seller_delete_on_Item_Data_delete_Trigger
        AFTER DELETE On Item_Data
        BEGIN
            DELETE FROM Seller WHERE id = OLD.seller AND (SELECT COUNT(*) FROM Item_Updatable_Data it_up_d 
                          JOIN Item_Data it_d ON it_d.id == it_up_d.ItemDataKey
                          JOIN Seller sl ON sl.id == it_d.seller 
                          WHERE sl.id = OLD.seller) == 0;
        END;
            """)
            
    '''

    # Update at 27/12/2024: TODO: Добавить триггер, удаляющий Item_Data запись при удалении из Item_Url


    # Создаю таблицу для хранения цен, продаж и возвратов

    # Если удаляется запись в таблице Item_Data, то и все записи в таблице Item_Updatable_Data тоже будут удалены
    cursor.execute("""
        CREATE TABLE Item_Updatable_Data (
            id UUID PRIMARY KEY NOT NULL,
            price INTEGER,
            soldCount INTEGER,
            refundCount INTEGER,
            ItemDataKey UUID,
            creationDateTime TIMESTAMP DEFAULT (datetime('now','localtime')),
            FOREIGN KEY(ItemDataKey) REFERENCES Item_Data(id) ON DELETE CASCADE
            );""")

    # TODO: Updated at 26/01/2025: Данные столбца updatedDateTime таблицы Item_Data не обновляются при парсинге данных Updatable_Item_Data. Решить баг с обновлением DateTime (Выполнено at 26/01/2025)

    # Внимание: при использовании скрипта для копирования данных 'PlatiMarket_Database_Migrate_Data.py' данные поле updatedDateTime будут указаны на момент выполнения скрипта, а не перенесены из базы данных
    # Updated at 28/01/2025: Чтобы исправить этот момент, заменил updatedDateTime = STRFTIME('%Y-%m-%d %H:%M:%S', 'NOW', 'localtime') на updatedDateTime = NEW.CreationDateTime
    # Таким образом, обновленное значение будет соответствовать дате создания новой записи обновляемых данных, что более корректно!

    # Создаю триггер для автоматического обновления updatedDateTime, вызываемое при обновлении записи
    cursor.execute("""
    CREATE TRIGGER Item_Data_timestamp_update_Trigger
    AFTER INSERT On Item_Updatable_Data
    BEGIN
       UPDATE Item_Data SET updatedDateTime = NEW.CreationDateTime WHERE id = NEW.ItemDataKey;
    END;
        """)


    # Код до внесения корректировки. На всякий случай!

    # cursor.execute("""
    #     CREATE TRIGGER Item_Data_timestamp_update_Trigger
    #     AFTER Update On Item_Updatable_Data
    #     BEGIN
    #        UPDATE Item_Data SET updatedDateTime = STRFTIME('%Y-%m-%d %H:%M:%S', 'NOW', 'localtime') WHERE id = NEW.id;
    #     END;
    #         """)


    # FOREIGN KEY всегда указываются после создания всех полей
    # Если необходимо создать One-to-One связь, то использую UNIQUE
    # У url товара может быть только одна запись с информацией, как и у записи может быть только один url товара

    # Если запись в Item_Data будет удалена, то и Item_Url запись тоже будет удалена
    cursor.execute("""
    CREATE TABLE Item_Url (
        id UUID PRIMARY KEY NOT NULL,
        url TEXT,
        data UUID UNIQUE,
        creationDateTime TIMESTAMP DEFAULT (datetime('now','localtime')),
        FOREIGN KEY(data) REFERENCES Item_Data(id) ON DELETE CASCADE
        );""")

    # На момент взаимодействия с базой данных закрывать соединение нельзя
    # Иначе будет выведена ошибка: sqlite3.ProgrammingError: Cannot operate on a closed cursor.

    # cursor.close()

    print('База данных необходимой структуры была успешно создана...\n')

    return sqliteConnection, cursor


def buildSqlConnection(db_name: str ='database.db') -> tuple:
    """
       buildSqlConnection: function

       Eng:
           builds connection to already existing database

       Rus:
           подключается к уже существующей базе данных

       Args:
           db_name (str): name of database (or path)

       Returns:
           tuple:
               sqliteConnection (sqlite3.Connection): object to operate with current database connection
               cursor (sqlite3.Cursor): object to operate with database
    """


    sqliteConnection = sqlite3.connect(db_name)
    cursor = sqliteConnection.cursor()

    return sqliteConnection, cursor

def closeSqlConnection(sqlite_connection: sqlite3.Connection,) -> None:
    """
       closeSqlConnection: function

       Eng:
           closes connection to database

       Rus:
           закрывает соединение с базой данных

       Args:
           sqlite_connection (sqlite3.Connection): object to operate with current database connection

       Returns:
           None
    """

    sqlite_connection.close()

    print('\nСоединение с базой данных успешно закрыто...')