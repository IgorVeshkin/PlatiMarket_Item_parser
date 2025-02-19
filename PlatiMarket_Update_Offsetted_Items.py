# Скрипт создан 21/01/2025
# Задача скрипта обновление актуальных данных товаров в базе данных, но с пременением смещения данных
# Скрипт необходимо запускать в случае если выполнение скрипта 'PlatiMarket_Update_Items.py' не было завершено корректно (не все записи были обновлены)

import time

# Импорт BeautifulSoup - библиотеки для парсинга данных с web-страницы
from bs4 import BeautifulSoup
# Импорт Selenium - библиотеки для автоматизированого взаимодействия со страницей
from selenium import webdriver

# Импорт regexp для получения данных из строк с помощью регулярных выражений
import re

# Импорт для проверки наличия файла базы данных
import os

# Импорт функции создания базы данных, построения связи и закрытия связи. Свои функции
from DatabaseOperation.databaseBasicOperations import createDatabase, buildSqlConnection, closeSqlConnection

# Импорт функции проверки наличия записи в базе и создания записи базы данных. Свои функции
from DatabaseOperation.databaseInteractionOperations import updateRecordData, getRecordUpdatableData, getOffsetProductUrls, getProductsCount


def parserReload(url_number: int, url_str: str, tries: int = 5, try_number: int = 1):
    if try_number > tries:
        print('\nПревышен лимит загрузок страницу. Закрытие программы...')

        return None, None, None, None, None, None, None, None

    print(f'\nПерезагружаю страницу {url_number}, ожидайте....')

    print(f'\nПопытка №{try_number}...')

    print(f'\nПарсер перезагрузится через {try_number*10} секунд(ы)...')

    # Ожидаю перед последующим запуском парсера
    time.sleep(try_number*10)

    # Создаем объект selenuim
    driver = webdriver.Edge()

    # Переходим на сайт
    driver.get(url_str)

    # Передаем html-код страницы в BeautifulSoup и создаем объект на основе полученных данных
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Получаем тело страницы
    body = soup.body

    try:
        # Название товара
        product_name = body.find('div', {'class': 'goods_descr_top--zag'}).h1.text
        # Цена товара
        product_price = body.find('i', {'id': 'product_price'}).text
        # Данные о проданных товарах
        product_sell_data = body.find('div', {'class': 'goods-sell-count'}).text

        # Получаю числовые данные из строки следующего содержания:

        # Продаж: 12
        #
        # Возвратов: 0
        #
        # Загружен: 28.09.2024

        extracted_sell_data = re.findall(r'\b\d+\b', product_sell_data)

        # Поскольку необходимы только значения продаж и возвратов сокращаем полученный массив чисел
        product_sell_count, product_refund_count = extracted_sell_data[:2]

        # Получаю данные продавца товара
        product_seller = body.find('a', {'class': 'goods_merchant_name'})
        # Имя продавца
        product_seller_name = product_seller.text
        # Ссылка на аккаунт продавца
        product_seller_url = product_seller.get('href')

        # Если url ссылка на аккаунт продавца товара начинается с /,
        # то удаляем этот символ для дальнейшего формирования полноценной ссылки
        if product_seller_url.startswith('/'):
            product_seller_url = product_seller_url[1:]

        # Ссылка на изображение товара
        product_image_url = body.find('div', {'class': 'goods_descr_images'}).a.img.get('src')

        # Если url ссылка на изображения товара начинается с //, то удаляем эти символы для удобства хранения
        if product_image_url.startswith('//'):
            product_image_url = product_image_url[2:]

        # Допиливаю ссылку, чтобы можно было перейти по ней прямо из терминала
        product_image_url = 'https://' + product_image_url

        # Основа ссылки, ведущая на сайт Plati Market
        url_base = 'https://plati.market/'

        # Ссылка на продавца
        product_seller_url = url_base + product_seller_url

        print('\nДанные успешно получены...')

        return product_name, product_price, product_sell_data, product_seller_name, product_seller_url, product_sell_count, product_refund_count, product_image_url

    except AttributeError:
        print('\nВнимание: элемент содержащий данные не был найден. Перезагружаю страницу...')

        return parserReload(url_number=url_number, url_str=url_str, tries=tries, try_number=try_number+1)


def main():
    # Основа ссылки, ведущая на сайт Plati Market
    url_base = 'https://plati.market/'

    # Название и/или путь до файла базы данных
    my_database_path = 'PlatiMarket_db.db'

    # Если база данных по указанному пути не найдена
    if not os.path.isfile(my_database_path):
        # Создаю базу данных определенной структуры
        sql_connection, sql_cursor = createDatabase(db_name=my_database_path)

        print('Поскольку база была только что создана, данных для автоматического обновления парсинга в ней быть не может. Инициирован выход из программы...')
        return

    # Если база существует, просто формируем подключение
    sql_connection, sql_cursor = buildSqlConnection(db_name=my_database_path)

    offset_right_limit = getProductsCount(cursor=sql_cursor)

    print('Данный скрипт \'PlatiMarket_Update_Offsetted_Items\' предназначен для запуска парсера обновления данных товаров, с момента на котором, по тем или иным причинам, прервался скрипт \'PlatiMarket_Update_Items\' '
          '\n\nИспользуйте номер последнего товара из вывода скрипта \'PlatiMarket_Update_Items\' \n\nПример строки с номером: \'Загружаю страницу 5, ожидайте....\', где 5 - номер товара\n')

    while True:
        user_offset = input(f'Введите номер товара, начиная с которого начнется обновление данных (диапозон от 1 до {offset_right_limit}): ').strip()

        try:
            user_offset = int(user_offset)
        except ValueError:
            print('\nВнимание: Введенное значение не является числом...\n')
            continue

        if user_offset <= 0 or user_offset > offset_right_limit:
            print(f'\nВнимание: Число должно обязательно входить в диапозон от 1 до {offset_right_limit}...\n')

            continue

        break


    try:
        data_uuids, db_urls = getOffsetProductUrls(cursor=sql_cursor, offset=(user_offset-1 if user_offset > 0 else 0))
    except ValueError:
        print('\nВнимание: В базе данных не было обнаружено ни одной записи. '
              'Запустите скрипт парсинга \'PlatiMarket_Item_parser_v1.py\' для индивидуального добавления товара в базу...')

        return

    print('\nДанные url-адресов успешно получены...\n')
    print('Количество товаров в базе данных:', len(db_urls), end='\n')

    for (url_number, url), data_uuid in zip(enumerate(db_urls, start=1), data_uuids):

        print(f'\nЗагружаю страницу {url_number}, ожидайте....')
        # print('\nuuid товара:', data_uuid)
        # print('Ссылка на товар:', url)

        # Создаем объект selenuim
        driver = webdriver.Edge()

        # Переходим на сайт
        driver.get(url)

        # Передаем html-код страницы в BeautifulSoup и создаем объект на основе полученных данных
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Получаем тело страницы
        body = soup.body

        # Класс элемента хранящий <h1>-тег с названием товара: goods_descr_top--zag

        try:
            # Название товара
            product_name = body.find('div', {'class': 'goods_descr_top--zag'}).h1.text

            # Updated at 20/01/2025: Блок проверки прекращены ли продажи товара или нет (Начало Блока)
            buying_form = body.find('div', {'class': 'goods_order_form_buttons'})

            # Если в блоке найден текст сообщающий о прекращении продажи товара, то выхожу из программы
            if 'Продажа товара приостановлена' in str(buying_form):
                # Updated at 01/02/2025: на изображениях PlatiMarket_sales_are_cancelled_1.png и PlatiMarket_sales_are_cancelled_2.png показано, что используется элемент h1
                # Но Я заметил, что 01/02/2025 аккаунт продавца заблокирован на данный момент (https://plati.market/itm/signalis-steam-gift-auto-ru-ukr-kz-cis/4220344)
                # На странице данного формата используется h2 элемент
                # Изображения данного товара с заблокированным продавцом называются: 'PlatiMarket_sales_are_cancelled_{n}_NEW_01_02_2025_h2_usage.png', где n = 1,2,3

                # TODO: Updated at 01/02/2025: Перенести код проверки блокировки аккаунта продавца в скрипты PlatiMarket_Update_Items.py и PlatiMarket_Item_parser_v1.py (Выполнено at 02/02/2025)

                # Начало блока проверки заблокированного пользователя
                if not buying_form.h1:
                    print('\nВнимание:', buying_form.h2.text.strip().split("\n")[0])

                    # Получение блока данными продавца
                    seller_info = body.find('div', {'class': 'goods_merchant_info'})

                    # Поиск изображения с src-аттрибутом отключенного аккаунта продавца
                    disabled_seller_img = seller_info.find('img', src='/img/icon-merchant-disabled.png')

                    # Если изображение найдено, то вывожу сообщение о том что продавец заблокирован (Способ №1)
                    if disabled_seller_img:
                        print('\nВнимание: Аккаунт продавца заблокирован...')

                    # Если в блоке данных продавца найдена ссылка на изображение отключенного аккаунта, то вывожу сообщение о том что продавец заблокирован (Способ №2)
                    # if '/img/icon-merchant-disabled.png' in str(seller_info):
                    #     print('\nВнимание: Аккаунт продавца заблокирован...')

                    print(
                        f'\nПоскольку продажи товара \'{product_name}\' были прекращены, получить актуальные данные невозможно. Перехожу к следующему товару...')

                    continue

                # Конец блока проверки заблокированного пользователя

                print('\nВнимание:', buying_form.h1.text.strip().split("\n")[0])
                print(
                    f'\nПоскольку продажи товара \'{product_name}\' были прекращены, получить актуальные данные невозможно. Перехожу к следующему товару...')
                continue

            elif 'Этот товар закончился' in str(buying_form):
                print('\nВнимание:', buying_form.h1.text.strip().split("\n")[0])
                print(
                    f'\nПоскольку товар \'{product_name}\' закончился, получить актуальные данные невозможно. Перехожу к следующему товару...')
                continue

            # Блок проверки прекращены ли продажи товара или нет (Конец Блока)

            # Цена товара
            product_price = body.find('i', {'id': 'product_price'}).text
            # Данные о проданных товарах
            product_sell_data = body.find('div', {'class': 'goods-sell-count'}).text

            # Получаю числовые данные из строки следующего содержания:

            # Продаж: 12
            #
            # Возвратов: 0
            #
            # Загружен: 28.09.2024

            extracted_sell_data = re.findall(r'\b\d+\b', product_sell_data)

            # Поскольку необходимы только значения продаж и возвратов сокращаем полученный массив чисел
            product_sell_count, product_refund_count = extracted_sell_data[:2]

            # Получаю данные продавца товара
            product_seller = body.find('a', {'class': 'goods_merchant_name'})
            # Имя продавца
            product_seller_name = product_seller.text
            # Ссылка на аккаунт продавца
            product_seller_url = product_seller.get('href')

            # Если url ссылка на аккаунт продавца товара начинается с /,
            # то удаляем этот символ для дальнейшего формирования полноценной ссылки
            if product_seller_url.startswith('/'):
                product_seller_url = product_seller_url[1:]

            # Ссылка на изображение товара
            product_image_url = body.find('div', {'class': 'goods_descr_images'}).a.img.get('src')

            # Если url ссылка на изображения товара начинается с //, то удаляем эти символы для удобства хранения
            if product_image_url.startswith('//'):
                product_image_url = product_image_url[2:]

            # Допиливаю ссылку, чтобы можно было перейти по ней прямо из терминала
            product_image_url = 'https://' + product_image_url

            # Ссылка на продавца
            product_seller_url = url_base + product_seller_url

        except AttributeError:
            print('\nВнимание: элемент содержащий данные не был найден. Возможно сайт начал блокировать парсер...')

            # Закомментировал по причине переделывания кода

            # print('\nПопробуйте запустить парсер позже...')
            # return

            # Update at 31/12/2024: При выводе ошибки программа прекратит свою работу, из-за чего при повторном запуске придется производит парсинг с начала

            # TODO: Сделать перезапуск текущего парсинга, если вывело данную ошибку (31/12/2024) (Выполнено)

            product_name, product_price, product_sell_data, product_seller_name, product_seller_url, product_sell_count, product_refund_count, product_image_url = parserReload(
                url_number=url_number, url_str=url, tries=5)

        # Если при перезагрузки страницы так и не получилось получить данные, то закрываю программу
        # Поскольку product_name может быть None, только если все элементы, вроде product_price, тоже None, то их нет смысла проверять
        # Достаточно проверки product_name
        if product_name is None:
            return

        # При одном из прогонов выдало ошибку:

        # Traceback (most recent call last):
        #   File "D:\Documents\Python_files\PlatiMarket_Items_Monitoring_Website\PlatiMarket_Item_parser\PlatiMarket_Update_Items.py", line 259, in <module>
        #     main()
        #   File "D:\Documents\Python_files\PlatiMarket_Items_Monitoring_Website\PlatiMarket_Item_parser\PlatiMarket_Update_Items.py", line 250, in main
        #     updateRecordData(sql_connection, sql_cursor, parsed_data, data_id=data_uuid)
        #   File "D:\Documents\Python_files\PlatiMarket_Items_Monitoring_Website\PlatiMarket_Item_parser\DatabaseOperation\databaseInteractionOperations.py", line 119, in updateRecordData
        #     if (int(data['product_price']) == new_price
        #         ^^^^^^^^^^^^^^^^^^^^^^^^^^
        # ValueError: invalid literal for int() with base 10: ''

        # Возможно, проблема возникла при парсинге на сайте при неправильном считывании данных. Ошибка впервые

        # Вывод спарсенных данных товара в терминал
        print('\nСпарсенное название товара:', product_name)
        print('Спарсенная цена товара:', product_price + ' руб.')
        print('Спарсенное имя продавца товара:', product_seller_name)
        print('Спарсенная ссылка на аккаунт продавца товара:', product_seller_url)

        print('Спарсенное количество проданого товара:', product_sell_count)
        print('Спарсенное количество возвратов товара:', product_refund_count)

        print('Спарсенная ссылка на изображение товара:', product_image_url, end='\n\n')

        # Построение словаря данных
        parsed_data = dict(
            product_name=product_name,
            item_url=url,
            product_seller_name=product_seller_name,
            product_seller_url=product_seller_url,
            product_sell_count=product_sell_count,
            product_refund_count=product_refund_count,
            product_image_url=product_image_url,
            product_price=product_price,

        )

        # Данные были спарсены проверка на существование базы данных была проведена при запуске программы
        # и данные для парсинга были взяты из базы данных,
        # проверка по аналогии с 'PlatiMarket_Item_parser_v1.py' не требуется

        updateRecordData(sql_connection, sql_cursor, parsed_data, data_id=data_uuid)

        getRecordUpdatableData(sql_cursor, data_uuid)


    closeSqlConnection(sqlite_connection=sql_connection)


if __name__ == '__main__':
    main()
