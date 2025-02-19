import sqlite3
import uuid

def main():
    sqliteConnection = sqlite3.connect('database.db')

    cursor = sqliteConnection.cursor()

    # Создаю UUID для продавца

    # Чтобы избежать ошибку: sqlite3.ProgrammingError: Error binding parameter 1: type 'UUID' is not supported
    # Необходимо перевести uuid в string с помощью метода str()
    seller_id = str(uuid.uuid4())

    # Пример добавления записи: https://stackoverflow.com/questions/6242756/how-to-retrieve-inserted-id-after-inserting-row-in-sqlite-using-python
    cursor.execute("""
        INSERT INTO Seller (id, name, accountURL) VALUES (?, ?, ?)
        """, (seller_id, 'CoTHuK', 'https://plati.market/seller/cothuk/889182/'))

    sqliteConnection.commit()

    # Создаю UUID для данных товара Item_Data
    data_id = str(uuid.uuid4())

    cursor.execute("""
            INSERT INTO Item_Data (id, name, seller, soldCount, refundCount, ImageURL) VALUES (?, ?, ?, ?, ?, ?)
            """, (data_id, '✅ RESIDENT EVIL 4 Deluxe REMAKE КЛЮЧ XBOX SERIES ✅ 🔑', seller_id, 12, 0, 'https://digiseller.mycdn.ink/preview/889182/p1_4654421_9bab21b0.jpg'))

    sqliteConnection.commit()

    # Создаю UUID для цены товара Item_Price
    price_id = str(uuid.uuid4())

    # Создаю запись цены
    cursor.execute("""
            INSERT INTO Item_Price (id, price, ItemDataKey) VALUES (?, ?, ?)
            """, (price_id, 2367, data_id))

    # Созданию UUID для ссылки товара Item_Url
    url_id = str(uuid.uuid4())

    cursor.execute("""
            INSERT INTO Item_Url (id, url, data) VALUES (?, ?, ?)
            """, (url_id, 'https://plati.market/https://plati.market/itm/resident-evil-4-deluxe-remake-kljuch-xbox-series/4654421', data_id))

    sqliteConnection.commit()

    cursor.close()

    print('Создание новой записи таблицы прошло успешно...')

if __name__ == '__main__':
    main()