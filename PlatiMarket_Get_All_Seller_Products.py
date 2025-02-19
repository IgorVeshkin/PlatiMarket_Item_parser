# Данные скрипт предназначен для получения всех товаров в базе данных определенного продавца

# Импорт функции создания базы данных, построения связи и закрытия связи. Своя функция
from DatabaseOperation.databaseBasicOperations import createDatabase, buildSqlConnection, closeSqlConnection

# Импорт функции получения данных продукта
from DatabaseOperation.databaseInteractionOperations import getSellerAllProduct

# Импорт для проверки наличия файла базы данных
import os

def main():
    # Название и/или путь до файла базы данных
    my_database_path = 'PlatiMarket_db.db'

    # Если база данных по указанному пути не найдена
    if not os.path.isfile(my_database_path):
        # Создаю базу данных определенной структуры
        sql_connection, sql_cursor = createDatabase(db_name=my_database_path)

        print(
            'Поскольку база была только что создана, данных для автоматического обновления парсинга в ней быть не может. Инициирован выход из программы...')
        return
    else:
        # Если база существует, просто формируем подключение
        sql_connection, sql_cursor = buildSqlConnection(db_name=my_database_path)

    # Вывод пояснительной информации
    print('Узнать id продавца можно с помощью специализированных программ, способных отображать данные баз данных...\n')

    # Ввожу следующую конструкцию
    while True:
        seller_id = input('Введите id продавца, список товаров которого хотите получить: ')

        # Если в переменную ссылки не было передано текста вообще
        # или переданна только неопределенная последовательность пробелов
        if not seller_id or seller_id.strip() == '':
            print(
                '\nВнимание: Вы не ввели id продавца на Plati Market. Введите id продавца...\n')

            continue

        break

    seller_product_data = getSellerAllProduct(cursor=sql_cursor, seller_id=seller_id)

    if seller_product_data is None:

        print('\nПродавец не был найден...')

        # Закрываю соединение с базой данных
        closeSqlConnection(sqlite_connection=sql_connection)

        # Прекращаю работу скрипта
        return

    seller_name, seller_url = seller_product_data['seller_name'], seller_product_data['seller_url']

    print('\nИмя продавца:', seller_name)
    print('Ссылка на аккаунт продавца:', seller_url, end='\n\n')

    for product_name, product_url in seller_product_data['products']:
        print('Название товара:', product_name)
        print('Ссылка на товар:', product_url, end='\n\n')

    # Закрываю соединение с базой данных
    closeSqlConnection(sqlite_connection=sql_connection)


if __name__ == '__main__':
    main()
