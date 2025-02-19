import sqlite3
import uuid


def main():
    sqliteConnection = sqlite3.connect('database.db')

    cursor = sqliteConnection.cursor()

    print(type(sqliteConnection), type(cursor))

    # Обновляю запись продавца
    # Ошибка: sqlite3.OperationalError: no such column: id
    # Для решении ошибки пришлось отредактировать структуру базы
    # Связь ForeignKEy в Item_Data была в виде FOREIGN KEY(seller) REFERENCES Seller(id), а в Seller поля id не было, только uuid
    # Поменял uuid на id в таблице Seller

    # uuid выбран для примера из базы данных
    cursor.execute('UPDATE Seller SET name = ? WHERE id = ?', ("CoTHuK", '25d01888-a764-4e2d-b955-5d21cea5e9b5',))

    # Обновление данных товара работает
    # Изменения поля updatedDateTime работает

    # Закомментировано. Использовалось для проверки
    # cursor.execute('UPDATE Item_Data SET soldCount = ? WHERE id = ?',
    #                (12, '424562e0-d9eb-4095-b36a-20e0243f0b30',))


    # Пример получения данных из таблицы Seller
    # cursor.execute('SELECT * FROM Seller WHERE uuid = ?', ('376d5a67-d550-4397-bb9f-74249f05a8fa',))

    # Чтобы избежать ошибки: sqlite3.OperationalError: ambiguous column name: id
    # необходимо указать уникальный id, то есть в WHERE id = ? заменить на WHERE Item_Price.id = ? (Указать однозначно)
    cursor.execute("""SELECT Item_Data.name, Item_Data.soldCount, Item_Data.refundCount, Item_Price.price, Item_Data.ImageURL, Seller.name, Seller.accountURL
                            FROM Item_Price 
                            LEFT JOIN Item_Data ON Item_Data.id=Item_Price.ItemDataKey 
                            LEFT JOIN Seller ON Seller.id=Item_Data.Seller 
                            WHERE Item_Price.id = ?""", ('6011ee13-410c-432f-92ef-6f47bafca385',))

    # Вывод полученных данных
    print(cursor.fetchall())

    # Создаю UUID для данных товара Item_Updatable_Data
    # price_id = str(uuid.uuid4())

    # Создание 2-ой записи цены для записи данных товара
    # cursor.execute("""INSERT INTO Item_Price (id, price, ItemDataKey) VALUES (?, ?, ?)""",
    #                (price_id, 2349, 'df4be930-5dc7-4baa-856e-27a928cc47c5',))

    # Вывод всех записей цен для определенной записи данных товара
    cursor.execute("""SELECT Item_Data.name, Item_Data.soldCount, Item_Data.refundCount, Item_Price.price, Item_Data.ImageURL, Seller.name, Seller.accountURL
                                FROM Item_Price 
                                LEFT JOIN Item_Data ON Item_Data.id=Item_Price.ItemDataKey 
                                LEFT JOIN Seller ON Seller.id=Item_Data.Seller 
                                WHERE Item_Data.id = ? """, ('df4be930-5dc7-4baa-856e-27a928cc47c5',))

    # Вывод полученных данных
    print(cursor.fetchall())




    sqliteConnection.commit()

    sqliteConnection.close()

    print('Запись продавца была успешно обновлена...')

if __name__ == '__main__':
    main()
