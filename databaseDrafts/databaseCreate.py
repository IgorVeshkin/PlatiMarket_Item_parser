import sqlite3

import os

def main():
    # if not os.path.isfile('database.db'):
    print('База данных не была найдена...\n')
    print('Создаю новую базу данных необходимой структуры...\n')

    sqliteConnection = sqlite3.connect('database.db')

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
    cursor.execute("""
    CREATE TRIGGER Seller_timestamp_update_Trigger
    AFTER UPDATE On Seller
    BEGIN
       UPDATE Seller SET updatedDateTime = STRFTIME('%Y-%m-%d %H:%M:%S', 'NOW', 'localtime') WHERE id = NEW.id;
    END;
        """)

    # FOREIGN KEY - это связь типа One-to-Many
    # У записи с информацией товара может быть только один продавец, тип связи One-to-One
    cursor.execute("""
    CREATE TABLE Item_Data (
        id UUID PRIMARY KEY NOT NULL,
        name VARCHAR(255),
        seller UUID UNIQUE,
        soldCount INTEGER,
        refundCount INTEGER,
        ImageURL TEXT,
        creationDateTime TIMESTAMP DEFAULT (datetime('now','localtime')),
        updatedDateTime TIMESTAMP DEFAULT (datetime('now','localtime')),
        FOREIGN KEY(seller) REFERENCES Seller(id)
        );""")

    # Создаю таблицу для хранения цен
    cursor.execute("""
        CREATE TABLE Item_Price (
            id UUID PRIMARY KEY NOT NULL,
            price INTEGER,
            ItemDataKey UUID,
            creationDateTime TIMESTAMP DEFAULT (datetime('now','localtime')),
            FOREIGN KEY(ItemDataKey) REFERENCES Item_Data(id)
            );""")


    # Создаю триггер для автоматического обновления updatedDateTime, вызываемое при обновлении записи
    cursor.execute("""
    CREATE TRIGGER Item_Data_timestamp_update_Trigger
    AFTER UPDATE On Item_Data
    BEGIN
       UPDATE Item_Data SET updatedDateTime = STRFTIME('%Y-%m-%d %H:%M:%S', 'NOW', 'localtime') WHERE id = NEW.id;
    END;
        """)

    # FOREIGN KEY всегда указываются после создания всех полей
    # Если необходимо создать One-to-One связь, то использую UNIQUE
    # У url товара может быть только одна запись с информацией, как и у записи может быть только один url товара
    cursor.execute("""
    CREATE TABLE Item_Url (
        id UUID PRIMARY KEY NOT NULL,
        url TEXT,
        data UUID UNIQUE,
        creationDateTime TIMESTAMP DEFAULT (datetime('now','localtime')),
        FOREIGN KEY(data) REFERENCES Item_Data(id)
        );""")

    cursor.close()

    print('База данных необходимой структуры была успешно создана...\n')

if __name__ == '__main__':
    main()