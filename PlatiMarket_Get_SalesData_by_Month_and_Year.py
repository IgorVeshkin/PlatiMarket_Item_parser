# Данные скрипт предназначен для получения данных продаж текущего товара, разбитых по месяцам

# Импорт функции создания базы данных, построения связи и закрытия связи. Своя функция
from DatabaseOperation.databaseBasicOperations import createDatabase, buildSqlConnection, closeSqlConnection

# Импорт функции получения данных продукта
from DatabaseOperation.databaseInteractionOperations import getAllProductUrls, getProductAllUpdatableDataDate, \
    getProductSellCount, getProductBasicData

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


    # getAllProductUrls возвращает связку id_товара и ссылка_товара,
    # ссылки мне не нужны, но поскольку функция возвращает id, то использую ее
    data_uuids, data_urls = getAllProductUrls(sql_cursor)

    # словарь для перевода месяцев форму слов
    month_converter_dict = {'01': 'январе',
                            '02': 'феврале',
                            '03': 'марте',
                            '04': 'апреле',
                            '05': 'мае',
                            '06': 'июне',
                            '07': 'июле',
                            '08': 'августе',
                            '09': 'сентябре',
                            '10': 'октябре',
                            '11': 'ноябре',
                            '12': 'декабре'}

    for data_id in data_uuids:

        dates = getProductAllUpdatableDataDate(cursor=sql_cursor, data_id=data_id)

        basic_product_data = getProductBasicData(cursor=sql_cursor, data_id=data_id)

        print(f'\nНазвание товара: {basic_product_data['product_name']}')
        print(f'Продавец: {basic_product_data['seller_name']}')
        print(f'Ссылка на товар: {basic_product_data['product_url']}')
        print(f'Ссылка на продавеца: {basic_product_data['seller_url']}')

        print(f'\nДата(ы) (месяц/год) для товара с id \'{data_id}\':\n')

        for month, year in dates:
            sellCount = getProductSellCount(cursor=sql_cursor, month=month, year=year, data_id=data_id)

            print(f'Количество продаж в {month_converter_dict[month]} {year} года:', sellCount)

        print()


    # Закрываю соединение с базой данных
    closeSqlConnection(sqlite_connection=sql_connection)

if __name__ == "__main__":
    main()
