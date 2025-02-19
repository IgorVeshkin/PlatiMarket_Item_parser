import sqlite3
import uuid

def checkRecord(cursor: sqlite3.Cursor, data: dict) -> [str, None]:
    """
        checkRecord: function

        Eng:
            checks by url product record existence in database

        Rus:
            проверяет наличие записи продукта в базе данных по url

        Args:
            cursor (sqlite3.Cursor): object to operate with database
            data (dict): data in which product url is found

        Returns:
            str: found uuid of Data_Item table record
            None
    """


    print(f'\nПроверка базы данных на наличие умеющейся записи товара по ссылке: {data['item_url']}')

    # Решение: https://stackoverflow.com/questions/20063718/python-sqlite3-how-to-use-like-and-to-do-partial-matching

    # Сравнение двух ссылок можно произвести только через оператор LIKE и конструкции '%{}%'
    cursor.execute('SELECT data, url FROM Item_Url WHERE url Like ?', ('%{}%'.format(data['item_url']), ))

    matched_data = cursor.fetchall()

    # Подразумивается, что все добавления в базу данных и все взаимодействие в целом будет производиться через приложение
    # В таком случае будет найдена только одна ссылка

    # Если list пустой, то выведет ошибку: IndexError: list index out of range
    # Использую matched_data[0][1] только с проверкой массива на наличие элементов
    print('\nСовпадающий url-адрес товара в базе данных:', matched_data[0][1] if matched_data else [])

    if len(matched_data) >= 1:
        return matched_data[0][0]
    else:
        return None


def checkSellerExistence(cursor: sqlite3.Cursor, seller_name: str) -> [str, None]:
    """
        checkSellerExistence: function

        Eng:
            checks seller record existence in database

        Rus:
            проверяет наличие записи продавца в базе данных

        Args:
            cursor (sqlite3.Cursor): object to operate with database
            seller_name (str): seller's name

        Returns:
            str: found uuid of seller record
            None
    """


    print(f'\nПроверка базы данных на наличие умеющейся записи продавца с именем \'{seller_name}\'...')

    # Ошибка: sqlite3.ProgrammingError: Incorrect number of bindings supplied. The current statement uses 1, and there are 7 supplied.
    # Ошибка возникает в случае если передать seller_name как переменную, а нужно tuple формата (seller_name, )
    cursor.execute('SELECT id FROM Seller WHERE name = ?', (seller_name, ))

    matched_seller = cursor.fetchall()

    if len(matched_seller) >= 1:
        print(f'\nПродавец с именем \'{seller_name}\' обнаружен. Новая запись для продавца создаваться не будет...')
        return matched_seller[0][0]
    else:
        return None


def createRecord(sqlite_connection: sqlite3.Connection, cursor: sqlite3.Cursor, data: dict) -> None:
    """
        createRecord: function

        Eng:
            creates new product record (several records across all tables of database and binds them together)

        Rus:
            создает новую запись продукта (несколько записей во всех таблицах базы данных и связывает их между собой)

        Args:
            sqlite_connection (sqlite3.Connection): object to operate with current database connection
            cursor (sqlite3.Cursor): object to operate with database
            data (dict): data to create new records across all database tables

        Returns:
            None
    """


    # Проверяю был ли продавец добавлен в базу данных ранее, при добавление других товаров
    seller_id = checkSellerExistence(cursor=cursor, seller_name=data['product_seller_name'])

    # Если продавец не найден, создаю новую запись
    if seller_id is None:

        # Создаю UUID для продавца

        # Чтобы избежать ошибку: sqlite3.ProgrammingError: Error binding parameter 1: type 'UUID' is not supported
        # Необходимо перевести uuid в string с помощью метода str()

        seller_id = str(uuid.uuid4())

        # Пример добавления записи: https://stackoverflow.com/questions/6242756/how-to-retrieve-inserted-id-after-inserting-row-in-sqlite-using-python
        cursor.execute("""
            INSERT INTO Seller (id, name, accountURL) VALUES (?, ?, ?)
            """, (seller_id, data['product_seller_name'], data['product_seller_url']))

        sqlite_connection.commit()

    # Иначе использую полученный seller_id в при создание других записей

    # Создаю UUID для данных товара Item_Data
    data_id = str(uuid.uuid4())

    # Ошибка: sqlite3.IntegrityError: UNIQUE constraint failed: Item_Data.seller
    # Ошибка возникла по причине ошибки в базе данных необходимо убрать ключ UNIQUE в таблице Item_Data у поля seller
    cursor.execute("""
            INSERT INTO Item_Data (id, name, seller, ImageURL) VALUES (?, ?, ?, ?)
            """, (data_id, data['product_name'], seller_id, data['product_image_url']))

    sqlite_connection.commit()

    # Создаю UUID для цены товара Item_Updatable_Data
    price_id = str(uuid.uuid4())

    # Создаю запись цены
    cursor.execute("""
            INSERT INTO Item_Updatable_Data (id, price, soldCount, refundCount, ItemDataKey) VALUES (?, ?, ?, ?, ?)
            """, (price_id, data['product_price'], data['product_sell_count'], data['product_refund_count'], data_id))

    # Созданию UUID для ссылки товара Item_Url
    url_id = str(uuid.uuid4())

    cursor.execute("""
            INSERT INTO Item_Url (id, url, data) VALUES (?, ?, ?)
            """, (url_id, data['item_url'], data_id))

    sqlite_connection.commit()

    print('\nСоздание новой записи таблицы прошло успешно...')


def updateRecordData(sqlite_connection: sqlite3.Connection, cursor: sqlite3.Cursor, data: dict, data_id: str) -> None:
    """
        updateRecordData: function

        Eng:
            updates product record data (i.e. creates new record in Item_Updatable_Data table and binds to Item_Data record)

        Rus:
            обновляет данные записи продукта (то есть, создает новую запись в таблице Item_Updatable_Data и связывает ее с запись в таблице Item_Data)

        Args:
            sqlite_connection (sqlite3.Connection): object to operate with current database connection
            cursor (sqlite3.Cursor): object to operate with database
            data (dict): data to create new records across all database tables
            data_id (str): uuid of record that needs to be updated

        Returns:
            None
    """


    # Получаю данные предыдущей цены
    cursor.execute('SELECT price, soldCount, refundCount, creationDateTime FROM Item_Updatable_Data WHERE ItemDataKey = ? ORDER BY creationDateTime DESC LIMIT 1', (data_id,))

    # Результат fetchall() представляет собой массив n-элементых кортежей
    # Типа: [(price1, soldCount1, refundCount1, datetime1),], где n=4
    # Поэтому, в начале получаем первый элемент массива, он там и так один из-за LIMIT 1, первый элемент кортежа

    fetched_data = cursor.fetchall()

    # Формирую новые данные
    new_price = int(fetched_data[0][0])
    new_sold_count = int(fetched_data[0][1])
    new_refund_count = int(fetched_data[0][2])

    # Если цена, количество продаж и возвратов не изменилась, то прекращаю работу функции
    if (int(data['product_price']) == new_price
            and int(data['product_sell_count']) == new_sold_count
            and int(data['product_refund_count']) == new_refund_count):
        print('Данные цены, продаж и возвратов не изменились...')
        return

    # Создаю UUID для обновленной цены товара Item_Updatable_Data
    new_updatable_data_id = str(uuid.uuid4())

    # Создаю запись обновленной цены
    cursor.execute(' INSERT INTO Item_Updatable_Data (id, price, soldCount, refundCount, ItemDataKey) VALUES (?, ?, ?, ?, ?)', (new_updatable_data_id, data['product_price'], data['product_sell_count'], data['product_refund_count'], data_id,))

    # Делаю коммит созданной записи
    sqlite_connection.commit()

    print('Данные цены, продаж и возвратов были успешно обновлены...')


def getRecordUpdatableData(cursor: sqlite3.Cursor, data_id: str) -> None:
    """
        getRecordUpdatableData: function

        Eng:
            displays data of prices and sales counts and refunds counts for specific product

        Rus:
            выводит данные цен, количества продаж и возвратов для определенного товара

        Args:
            cursor (sqlite3.Cursor): object to operate with database
            data_id (str): record's uuid of which updatable data needs to be displayed

        Returns:
            None
    """


    # Получаю все цены определенного товара и другие редактируемые данные

    # Чтобы избежать ошибку типа: sqlite3.OperationalError: ambiguous column name: creationDateTime
    # Необходимо явно прописать таблицу элемента: заменить creationDateTime на Item_Updatable_Data.creationDateTime
    # Данная ошибка возникает если используется оператор JOIN
    # И есть необходимость указывать принадлежность того или иного столбца
    cursor.execute(
        """SELECT Item_Data.name, Item_Updatable_Data.price, Item_Updatable_Data.soldCount, Item_Updatable_Data.refundCount, Seller.name, Item_Updatable_Data.creationDateTime
        FROM Item_Updatable_Data 
        LEFT JOIN Item_Data ON Item_Data.id=Item_Updatable_Data.ItemDataKey
        LEFT JOIN Seller ON Seller.id=Item_Data.Seller
        WHERE ItemDataKey = ? 
        ORDER BY Item_Updatable_Data.creationDateTime DESC
        """,
        (data_id,))

    fetched_data = cursor.fetchall()

    print(f'\nНазвание: {fetched_data[0][0]}')
    print(f'Продавец: {fetched_data[0][4]}')
    print(f'Данные цены, продаж и возвратов полученного товара с id \'{data_id}\' в динамике:\n', )

    for record in fetched_data:
        print(record[5], '->', record[1], 'рублей', '|', 'Продажи:', record[2], '|', 'Возвратов:', record[3])

    # TODO: Сделать вывод (return) в виде списка (list)


def getAllProductUrls(cursor: sqlite3.Cursor) -> tuple[list, list]:
    """
        getAllProductUrls: function

        Eng:
            returns all products uuids and urls from Item_Url table

        Rus:
            возвращает идентификатары и url-ссылки всех товаров из таблицы Item_Url

        Args:
            cursor (sqlite3.Cursor): object to operate with database

        Returns:
            tuple: includes 2 list (first is data_uuids, second is products' urls)
    """


    # Получаю uuid данных товаров и ссылки товар на площадке Plati Market
    cursor.execute("""SELECT data, url FROM Item_Url""")

    products = dict(cursor.fetchall())

    # Вариант разделения ключей от значений №1
    # return list(products.keys()), list(products.values())

    # Вариант разделения ключей от значений №2

    keys, values = zip(*products.items())

    return keys, values


# Updated 21/01/2025: Добавляю функцию для получения ссылок на товары со сдвигом

def getOffsetProductUrls(cursor: sqlite3.Cursor, offset: int = 0) -> tuple[list, list]:
    """
        getOffsetProductUrls: function

        Eng:
            returns all products uuids and urls with applied offset from Item_Url table

        Rus:
            возвращает идентификатары и url-ссылки всех товаров с примененым смещением из таблицы Item_Url

        Args:
            cursor (sqlite3.Cursor): object to operate with database
            offset (int): value of offset (starting point) : optional (default: 0)

        Returns:
            tuple: includes 2 list (first is data_uuids, second is products' urls)
    """


    # Получаю uuid данных товаров и ссылки товар на площадке Plati Market, задавая сдвиг
    # Пример использования: Если работу парсера необходимо начать не с начала а с определенного элемента в случаях, если работа парсера была прервана

    # Текст ошибки:

    # cursor.execute("""SELECT data, url FROM Item_Url OFFSET ?""", (offset,))
    # sqlite3.OperationalError: near "?": syntax error

    # Нельзя использовать OFFSET без LIMIT, чтобы не выдать все записи таблицы LIMIT выставляю как -1
    cursor.execute("""SELECT data, url FROM Item_Url LIMIT -1 OFFSET ?""", (offset,))

    products = dict(cursor.fetchall())

    # Вариант разделения ключей от значений №2

    keys, values = zip(*products.items())

    return keys, values

def getProductsCount(cursor: sqlite3.Cursor,) -> int:
    # Получаю количество товаров в базе данных
    cursor.execute("""SELECT COUNT(*) FROM Item_Data""")

    # Возвращаю полученное значение
    return cursor.fetchone()[0]


def getProductAllUpdatableDataDate(cursor: sqlite3.Cursor, data_id: str) -> [tuple, None]:
    """
        getProductAllUpdatableDataDate: function

        Eng:
            returns dates (separated months and years) for all updatable data record from Item_Updatable_Data table for specific product record

        Rus:
            возвращает даты (месяцы и годы) для всех обновляемых записей данных из таблицы Item_Updatable_Data для конкретной записи продукта

        Args:
            cursor (sqlite3.Cursor): object to operate with database
            data_id (int): specific product record id from Item_Data table

        Returns:
            tuple: includes 2 list (first is data_uuids, second is products' urls)
            None
    """


    # Получаю уникальные месяцы и года всех обновляемых записей в таблице Item_Updatable_Data для определенного товара (sql-запрос №8)
    cursor.execute("""SELECT strftime('%m', creationDateTime), strftime('%Y', creationDateTime) 
                              FROM Item_Updatable_Data 
                              WHERE ItemDataKey = ?
                              GROUP BY strftime('%m', creationDateTime)
                              ORDER BY strftime('%Y', creationDateTime) """, (data_id,))


    date_data = cursor.fetchall()

    if not date_data:
        print(
            f'\nНе было найдено ни одной записи для товара c id \'{data_id}\'. Возможно товара с данным id не существует...')
        return None

    # Получение числа продаж для опреденной записи по датам типа месяц/год

    print(
        f'\nПолучение уникальных значений дат (месяц/год) для для товара c id \'{data_id}\' было успешно завершено...')

    return date_data


def getProductSellCount(cursor: sqlite3.Cursor, month: str, year: str, data_id: str) -> [int, None]:

    cursor.execute("""SELECT max(soldCount) - min(soldCount)
                                  FROM Item_Updatable_Data 
                                  WHERE strftime('%m', creationDateTime) = ? AND strftime('%Y', creationDateTime) = ?
                                  AND ItemDataKey = ?
                                  """, (month, year, data_id))

    # cursor.fetchone() возвращает данные структуры (None,), если не найдено совпадений, поэтому возвращаю [0],
    # чтобы получить первый элемент кортежа
    soldCount = cursor.fetchone()[0]

    # Конструкция if not soldCount срабатывает если sql-запрос возвращает 0 (ноль),
    # по этой причине заменил на явную проверку на None, то есть if soldCount is None
    if soldCount is None:
        print('\nДанные не найдены. Проверьте правильность введенных данных...')

        return None

    return int(soldCount)


def getProductBasicData(cursor: sqlite3.Cursor, data_id: str) -> [dict, None]:
    """
        getProductBasicData: function

        Eng:
            returns basic data of specific product

        Rus:
            возвращает основную информацию определенного продукта

        Args:
            cursor (sqlite3.Cursor): object to operate with database
            data_id (int): specific product record id from Item_Data table

        Returns:
            dict: data of product with structure (product_name, seller_name, product_url, seller_account_url)
            None
    """


    # Выполняю sql-запрос для получения данных
    cursor.execute("""SELECT dt.name, sl.name, url.url, sl.accountURL
                            FROM Item_Data dt
                            LEFT JOIN Seller sl ON sl.id=dt.Seller
                            LEFT JOIN Item_Url url ON dt.id=url.data
                            WHERE dt.id = ?
                            """, (data_id,))

    # cursor.fetchone() возвращает структуры типа:
    # (Название_товара, имя_продавца, ссылка_на_товар, ссылка_на_продавца)

    basic_data = cursor.fetchone()

    if basic_data is None:
        print('\nДанные не найдены. Проверьте правильность введенных данных...')

        return None

    # Формирую структуру словаря

    basic_data_dict = dict(product_name=basic_data[0], seller_name=basic_data[1], product_url=basic_data[2], seller_url=basic_data[3])

    return basic_data_dict


def getSellerAllProduct(cursor: sqlite3.Cursor, seller_id: str) -> [dict, None]:
    """
        getSellerAllProduct: function

        Eng:
            returns all products of specific seller

        Rus:
            возвращает все товары определенного продавца

        Args:
            cursor (sqlite3.Cursor): object to operate with database
            seller_id (str): specific seller record id from Seller table

        Returns:
            dict: data of products and their seller (seller_name, seller_url, (product_name, product_url))
            None
    """


    # Выполняю получение данных через два запроса,
    # чтобы не перенагружать повторяющейся информацией (именем продавца) второй запрос

    cursor.execute("""SELECT name, accountURL FROM SELLER WHERE id = ?""", (seller_id, ))

    try:
        seller_name, seller_url = cursor.fetchone()

    except TypeError:

        # Продавец не был найден...

        return None

    # Запрос через таблицу Item_Data (Данных продукта)
    cursor.execute("""SELECT itd.name, url_t.url
                              FROM Item_Data itd
                              INNER JOIN Item_Url url_t ON url_t.data = itd.id
                              WHERE itd.seller = ?""", (seller_id,))

    # Получаю данные товаров определенного продавца
    all_seller_products = cursor.fetchall()

    # Формирую словарь
    seller_products_dict = {'seller_name': seller_name, 'seller_url': seller_url, 'products': all_seller_products}

    return seller_products_dict


def deleteRecord(sqlite_connection: sqlite3.Connection, cursor: sqlite3.Cursor, data_uuid: str) -> None:
    """
        deleteRecord: function

        Eng:
            deletes product from database (also deletes seller if zero products of him remains)

        Rus:
            удаляет товар из базы данных (также удаляет продавца, если у него не осталось ни одного товара)

        Args:
            sqlite_connection (sqlite3.Connection): object to operate with current database connection
            cursor (sqlite3.Cursor): object to operate with database
            data_uuid (str): specific product record id from Item_Data table

        Returns:
            None
    """


    # Настройка необходима для корректной работы ON DELETE CASCADE при удаление FOREIGNKEY
    # Ее нужно запуска при каждом подключение
    # Можно перенести в функции createDatabase или buildSqlConnection,
    # но поскольку необходима, в моем случае, только при удалении, то вызываю непосредственно в функции удаления
    cursor.execute("""PRAGMA foreign_keys = ON""")

    # Получаю uuid продавца, чтобы проверить количество записей, связанных с ним
    cursor.execute("""SELECT seller FROM Item_Data WHERE id = ?""", (data_uuid,))

    # Заношу полученные данные в переменную seller_id
    seller_id = cursor.fetchone()[0]

    # Получаю количество записей связанных с продавцом
    cursor.execute("""SELECT Count(id) FROM Item_Data WHERE seller = ?""", (seller_id,))

    # Заношу в переменную
    seller_items_count = cursor.fetchone()[0]
    print(f'\nКоличество записей связанных с продавцом c id \'{seller_id}\':', seller_items_count, end='\n\n')

    # Происходит удаление только записи из таблицы Item_Data
    # Удаление из таблиц Item_Updatable_Data и Item_Url не производится

    # Два пути решения: поменять структуру базы данных либо реализовать удаление на уровне кода Python

    # Правильнее будет сделать удаление через sqlite поменяв структуры базы данных,
    # но тогда придется писать код для переноса данных из старой базы данных в новую (Выполнено)

    # TODO: Доработать структуры, чтобы работало автоматичесткое удаление записей во всех таблицах по цепочке (Выполнено)

    # Удаление записи из Item_Data
    cursor.execute("""DELETE FROM Item_Data WHERE id = ?""", (data_uuid,))
    # Подтверждение удаления
    sqlite_connection.commit()

    print('Запись товара успешно удалена...\n')

    # В databaseBasicOperations.py в функции createDatabase закомментирован триггер Seller_delete_on_Item_Data_delete_Trigger
    # Если он раскомментирован то нижеописанный код необходимо исключить, поскольку этот функционал будет исполняться на уровне базы данных
    # Переменную seller_items_count тоже будет необходимо исключить

    # Если запись только одна, то после удаления записи продавец не будет связан ни с одной записью товара
    if seller_items_count == 1:
        # В таком случае, удаляю данные продавца
        print('Продавец был связан, только с товаром, который был только что удален. В таком случае, удаляю и продавца...\n')

        cursor.execute("""DELETE FROM Seller WHERE id = ?""", (seller_id,))
        sqlite_connection.commit()

        print('Процесс удаления записи был успешно завершен...')

        return


    # Если продавца существует, то seller_item_count не может быть равен 0
    # Значит seller_item_count во всех других случаях больше 1
    # Только если база данных не была модифицирована стороними редакторами, вроде SQLiteStudio

    print('Продавец связан с несколькими записями помимо удаленной. Продавец не будет удален из базы данных...\n')

    print('Процесс удаления записи был успешно завершен...')

    # Временно размещаю эту информацию здесь. Допустим Я сделаю функционал удаления записи Item_Updatable_Data
    # Может сложиться ситуация, что с у записи в таблице Item_Data не будет ни одной связанной записи из Item_Updatable_Data
    # В таком случае необходимо либо удалять запись в Item_Data,
    # либо сделать проверку на наличие записей в функции getRecordUpdatableData
    # TODO: Решить вышеописаную задачу

    # Важное наблюдение: Если удалить запись через редактор SQLiteStudio, обладающую свойством ON DELETE CASCAD,
    # то записи из других таблиц, связанные с удаленной, тоже будут удалены

    # Если удалить Item_Data запись через SQLiteStudio, запись в Seller сохраниться.
    # TODO: Возможно есть смысл написать триггер через sqlite для удаления записи продавца Seller. Тогда не нужна будет проверка на Python (Выполнено)

    # Если удалить все записи Item_Updatable_Data определенной записи в Item_Data,
    # то при повторном парсинге в функции updateRecordData будет выведена ошибка: IndexError: list index out of range
    # TODO: Нужно сделать проверку, если будет реализован функционал удаления записей в Item_Updatable_Data
