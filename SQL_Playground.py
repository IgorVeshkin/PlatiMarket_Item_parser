# Мини-скрипт для проверки sql-запросов
# В частности: одного sql-запроса для подсчета всех записей из таблицы Item_Updatable_Data, связанных с определенным продавцом


from datetime import datetime

from DatabaseOperation.databaseBasicOperations import buildSqlConnection, closeSqlConnection

def main():

    # Название и/или путь до файла базы данных
    my_database_path = 'PlatiMarket_db.db'

    sql_connection, sql_cursor = buildSqlConnection(db_name=my_database_path)

    seller_id = '127dbc81-d271-4ffe-9eb3-3a23d9091397'

    # Вспомогательный sql-запрос для получения имени продавца
    sql_cursor.execute("""SELECT name FROM Seller WHERE id = ?""", (seller_id,))

    print('Имя продавца, для которого производится выполнение sql-запросов №1 и №2:', *sql_cursor.fetchone(), end='\n\n')

    # Sql-запрос №1
    # Получаю количество записей из Item_Updatable_Data, но может получиться так, что записей в Item_Updatable_Data
    # может и не быть, но записи в Item_Data есть, по этой причине добавил sql-запрос №2

    # id подбирается из базы для Seller
    sql_cursor.execute("""SELECT COUNT(*) FROM Item_Updatable_Data it_up_d 
                          JOIN Item_Data it_d ON it_d.id == it_up_d.ItemDataKey
                          JOIN Seller sl ON sl.id == it_d.seller 
                          WHERE sl.id=?""", (seller_id,))

    print('Количество записей из таблицы Item_Updatable_Data, связанных с продавцом (Количество апдейтов) (sql-запрос №1):', *sql_cursor.fetchone())


    # Sql-запрос №2
    # id подбирается из базы для Seller
    sql_cursor.execute("""SELECT COUNT(*) FROM Item_Data it_d 
                              JOIN Seller sl ON sl.id == it_d.seller 
                              WHERE sl.id=?""", (seller_id,))

    print('\nКоличество записей из таблицы Item_Data, связанных с продавцом (sql-запрос №2):', *sql_cursor.fetchone(), end='\n\n')

    # id записи из таблицы Item_Data
    item_data_id = '67bb0d30-758a-4b0f-b024-27fa8652f2c8'

    # Вспомогательный sql-запрос для получения имени товара
    sql_cursor.execute("""SELECT name FROM Item_Data WHERE id = ?""", (item_data_id,))

    print('Название товара, для которого производится выполнение sql-запросов №3 и №4:', *sql_cursor.fetchall(), end='\n\n')

    # Sql-запрос №3

    # Беру все записи из Item_Updatable_Data, и для каждой даты оставляем одну единственную запись с максимальной ценой
    sql_cursor.execute("""
                    SELECT max(price), t1 FROM (
                    SELECT price, DATE(creationDateTime) t1, TIME(creationDateTime) t2
                    FROM Item_Updatable_Data
                    WHERE ItemDataKey = ?
                    ) GROUP BY t1
                    """, (item_data_id,))

    print('Получение всех записей из Item_Updatable_Data и для каждой даты нахождение единственной записи с максимальной ценой (sql-запрос №3):\n')

    sql_request_3_data = sql_cursor.fetchall()

    for current_price, current_date in sql_request_3_data:
        print(f'Дата: {datetime.strptime(current_date, '%Y-%m-%d').strftime('%d/%m/%Y')}; Цена: {current_price} рублей\n')

    print('Всего записей sql-запроса №3:', len(sql_request_3_data), end='\n\n\n')


    # Sql-запрос №4

    # Беру все записи из Item_Updatable_Data и вывожу их всех
    sql_cursor.execute("""
                    SELECT price, DATE(creationDateTime), TIME(creationDateTime) FROM Item_Updatable_Data
                    WHERE ItemDataKey = ?
                    """, (item_data_id,))

    print(
        'Получение всех записей из Item_Updatable_Data и и вывожу их всех (sql-запрос №4):\n')


    sql_request_4_data = sql_cursor.fetchall()

    for current_price, current_date, current_time in sql_request_4_data:
        print(
            f'Дата: {datetime.strptime(current_date, '%Y-%m-%d').strftime('%d/%m/%Y')}; Время: {current_time}; Цена: {current_price} рублей\n')

    print('Всего записей sql-запроса №4:', len(sql_request_4_data))


    # Sql-запрос №5

    item_data_uuid = '2bcff64d-3fd1-4894-99a4-a80ec0590569'

    print('\n\nПолучение общего количества проданных единиц товара за все время (sql-запрос №5):')

    # Получаю количество проданного товара за все время

    # Поскольку количество проданного товара это разница между самой ранней и самой поздней записями продаж
    # и, поскольку, значение количества проданных копий товара может только расти,
    # то разницу можно найти как значение между максимальным и минимальным значением

    sql_cursor.execute("""
                        SELECT max(soldCount) - min(soldCount) FROM Item_Updatable_Data
                        WHERE ItemDataKey = ?
                        """, (item_data_uuid,))


    print(f'\nКоличество проданных единиц товара с id \'{item_data_uuid}\' за все время:', *sql_cursor.fetchone(),
          end='\n\n')

    # Sql-запрос №6

    print('\n\nПолучение общего количества проданных единиц товара за все время через даты создания записей (sql-запрос №6):')

    # Получаю количество проданного товара за все время

    # sqlite3.OperationalError: ORDER BY clause should come after UNION not before
    # Чтобы избежать следующую вышеописанную ошибку, необходимо запрос (SELECT soldCount FROM Item_Updatable_Data WHERE ItemDataKey = ? ORDER BY creationDateTime ASC LIMIT 1)
    # обернуть в SELECT * FROM (SQL_QUERY), где SQL_QUERY - это предыдущий запрос

    # Запись слишком грамосткая и мало чем отличается от sql-запроса №5, за исключением того, что я строго получаю две записи из таблицы

    sql_cursor.execute("""  
                            SELECT max(soldCount) - min(soldCount) FROM (
                            
                            SELECT soldCount FROM (SELECT soldCount FROM Item_Updatable_Data WHERE ItemDataKey = ? ORDER BY creationDateTime ASC LIMIT 1)
                            
                            UNION
                            
                            SELECT soldCount FROM (SELECT soldCount FROM Item_Updatable_Data WHERE ItemDataKey = ? ORDER BY creationDateTime DESC LIMIT 1)
                            
                            )
                            """, (item_data_uuid, item_data_uuid))

    print(f'\nКоличество проданных единиц товара с id \'{item_data_uuid}\' за все время (proof-of-concept):', *sql_cursor.fetchone(),
          end='\n\n\n')


    # Получаю уникальные месяцы и года всех записей в таблице Item_Updatable_Data
    sql_cursor.execute("""SELECT strftime('%m', creationDateTime), strftime('%Y', creationDateTime) 
                          FROM Item_Updatable_Data 
                          GROUP BY strftime('%m', creationDateTime)
                          ORDER BY strftime('%Y', creationDateTime) """)

    print('Получение уникальных значений месяцев и годов всех записей обновляемых данных в Item_Updatable_Data (sql-запрос №7):')

    for item in sql_cursor.fetchall():
        print(item)

    # Получаю уникальные месяцы и года всех обновляемых записей в таблице Item_Updatable_Data для определенного товара (sql-запрос №8)
    sql_cursor.execute("""SELECT strftime('%m', creationDateTime), strftime('%Y', creationDateTime) 
                          FROM Item_Updatable_Data 
                          WHERE ItemDataKey = ?
                          GROUP BY strftime('%m', creationDateTime)
                          ORDER BY strftime('%Y', creationDateTime) """, (item_data_uuid, ))


    # Запросы №8 и №9 подпадают под разработку функционала скрипта получения числа продаж для опреденной записи по датам типа месяц/год

    print(
        f'\nПолучение уникальных значений месяцев и годов всех записей обновляемых данных в Item_Updatable_Data для товара c id \'{item_data_uuid}\' (sql-запрос №8):')

    months_and_years = sql_cursor.fetchall()

    # Вывод уникальных комбинаций месяцев и годов, в которых были созданы записи цен, продаж и возвратов
    for month, year in months_and_years:
        print(month, year)


    print(f'\nПолучение количества продаж в определенный месяц и год для определенного товара с id \'{item_data_uuid}\' (sql-запрос №9):\n')

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

    for month, year in months_and_years:

        sql_cursor.execute("""SELECT max(soldCount) - min(soldCount) 
                              FROM Item_Updatable_Data 
                              WHERE strftime('%m', creationDateTime) = ? AND strftime('%Y', creationDateTime) = ?
                              AND ItemDataKey = ?
                              """, (month, year, item_data_uuid))

        print(f'Количество продаж в {month_converter_dict[month]} {year} года:', *sql_cursor.fetchone())


    # Получение всех записей товара одного продавца (sql-запрос №10)
    seller_id = '8f1a18f5-3529-4285-a46c-20d23b8962fe'

    # Запрос через таблицу Seller (продавца)
    # sql_cursor.execute("""SELECT itd.name, sl.name
    #                       FROM Seller sl
    #                       INNER JOIN Item_Data itd ON itd.seller = sl.id
    #                       WHERE sl.id = ?
    #                       """, (seller_id,))

    # Запрос через таблицу Item_Data (Данных продукта)
    sql_cursor.execute("""SELECT itd.name, sl.name, url_t.url
                          FROM Item_Data itd
                          INNER JOIN Seller sl ON sl.id = itd.seller
                          INNER JOIN Item_Url url_t ON url_t.data = itd.id
                          WHERE seller = ?""", (seller_id,))

    all_seller_products = sql_cursor.fetchall()

    print(f'\nВсе записи товаров продавца {all_seller_products[0][1]} (sql-запрос №10):\n')

    print(f'Количество найденных записей товаров продавца {all_seller_products[0][1]}:', len(all_seller_products), end='\n\n')

    for product in all_seller_products:
        print('Название:', product[0])
        print('Ссылка на товар:', product[2], end='\n\n')

    print('Получение имени и ссылки продавца (sql-запрос №11)...\n')

    sql_cursor.execute("""SELECT name, accountURL FROM SELLER WHERE id = ?""", (seller_id,))

    try:
        seller_name, seller_url = sql_cursor.fetchone()

        print('Имя продавца:', seller_name)
        print('Ссылка на аккаунт продавца:', seller_url)

    except TypeError as tp_error:

        print('Продавец не был найден...')
        print('\nТекст ошибка:', tp_error)


    # Получение средней цены товара по датам формата 'месяц/год' за целый месяц (sql-запрос №12)

    # В базе данных цена фиксируется только если она корректируется продавцом,
    # поэтому большой вопрос актуальны ли данные показатели
    # Далее приведен пример более точного подсчета, в котором используется заполнение пропущенных дат

    print(f'\n\nСредняя цена товара с id \'{item_data_uuid}\' по месяцам (sql-запрос №12): \n')

    # Получаю уникальные месяцы и года всех обновляемых записей в таблице Item_Updatable_Data для определенного товара
    sql_cursor.execute("""SELECT strftime('%m', creationDateTime), strftime('%Y', creationDateTime) 
                             FROM Item_Updatable_Data 
                             WHERE ItemDataKey = ?
                             GROUP BY strftime('%m', creationDateTime)
                             ORDER BY strftime('%Y', creationDateTime) """, (item_data_uuid,))


    unique_dates = sql_cursor.fetchall()

    for month, year in unique_dates:

        sql_cursor.execute("""SELECT round(avg(price), 2)
                              FROM Item_Updatable_Data 
                              WHERE strftime('%m', creationDateTime) = ? AND strftime('%Y', creationDateTime) = ?
                              AND ItemDataKey = ?
                              """, (month, year, item_data_uuid))

        print(f'Средняя цена товара в {month_converter_dict[month]} {year} года:', *sql_cursor.fetchone(), 'руб.')


    print()

    # Подсчет средней цены с заполнением пропусков в датах (Если определенный день пропущен в диапозоне, то добавляется цена за предыдущий день)

    print('Подсчет средней цены с заполнением пропусков в датах (Если определенный день пропущен в диапозоне, то добавляется цена за предыдущий день)...\n')

    for month, year in unique_dates:

        prices_by_days = []

        sql_cursor.execute("""SELECT price, strftime('%d/%m/%Y', creationDateTime)
                                      FROM Item_Updatable_Data
                                      WHERE strftime('%m', creationDateTime) = ? AND strftime('%Y', creationDateTime) = ?
                                      AND ItemDataKey = ?
                                      """, (month, year, item_data_uuid))

        dt = sql_cursor.fetchall()
        print('Массив до заполнения пробелов (формат: цена/дата):', dt)
        print('Длина массива до заполнения пробелов:', len(dt), end='\n\n')

        sql_cursor.execute("""SELECT price, strftime('%d', creationDateTime), strftime('%d/%m/%Y', creationDateTime)
                              FROM Item_Updatable_Data 
                              WHERE strftime('%m', creationDateTime) = ? AND strftime('%Y', creationDateTime) = ?
                              AND ItemDataKey = ?
                              """, (month, year, item_data_uuid))

        prices = sql_cursor.fetchall()

        for index in range(len(prices)):
            # Если не столкнулся с концом массива

            if index+1 < len(prices):
                # Получаю разницу по дням
                days_diff = int(prices[index+1][1]) - int(prices[index][1])

                # Если разница больше одного дня (например, 14/01/2025 и 17/01/2025 => 17 - 14 = 3)
                if days_diff > 1:
                    # Запускаю цикл, выполняющий работу пока разница не сократится до одного дня (между датами не будет пустых дней)
                    current_price = prices[index][0]
                    current_day = int(prices[index][1])
                    while days_diff >= 1:
                        # Добавляю текущую дату (цена в промежутках не менялась)
                        prices_by_days.append((current_price , current_day))
                        # Сокращаю прогал на один день
                        days_diff = days_diff - 1
                        current_day = current_day + 1


                # Если разница составляет один день или обе проверки произошли в один день, то добавляю текущую цену
                elif days_diff == 0:
                    prices_by_days.append((prices[index][0], int(prices[index][1])))

                elif days_diff == 1:
                    prices_by_days.append((prices[index][0], int(prices[index][1])))

            else:
                prices_by_days.append((prices[index][0], int(prices[index][1])))

        print('Массив до заполнения пробелов (формат: цена/день):', prices_by_days)
        print('Длина массива после заполнения пробелов:', len(prices_by_days), end='\n\n')

        print()

        # Поскольку может возникнуть ситуация, при которой проверка данные производилась несколько раз за день и данные менялись,
        # то необходимо находить среднее значение для даннных с одинаковыми днями

        unique_days = set(map(lambda x: x[1], prices_by_days))
        grouped_prices_by_day = [[price for price, day in prices_by_days if day==u_day] for u_day in unique_days]

        print('Сгруппированные цены по дням:')
        print('grouped_prices_by_day:', grouped_prices_by_day, end='\n\n')

        prices_sums = [sum(pr)/len(pr) if len(pr) > 1 else pr[0] for pr in grouped_prices_by_day]

        print('Цены, у которых найдено среднее значение если обнаружено несколько записей за один день:')
        print('prices_sums:', prices_sums, end='\n\n')

        print(f'Средняя цена товара в {month_converter_dict[month]} {year} года:', round(sum(list(map(lambda x: x[0], prices_by_days)))/len(prices_by_days), 2), 'руб.')

        print(f'Средняя цена товара в {month_converter_dict[month]} {year} года (с учетом нескольких записей за один день):', round(sum(prices_sums)/len(prices_sums), 2), 'руб.\n')

    closeSqlConnection(sql_connection)


if __name__=='__main__':
    main()