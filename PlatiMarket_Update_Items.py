# Данный файл предназначен для автоматического обновления данных всех имеющихся записей в базе данных
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
from DatabaseOperation.databaseInteractionOperations import updateRecordData, getRecordUpdatableData, getAllProductUrls

# Updated at 31/12/2024: Добавил функцию для автоматической перезагрузки парсера при возникновении ошибок получения данных парсера
# При прогонах программа 31/12/2024 при возникновении проблем, программа успешно загружала данные при перезагрузке с первой попытки

# Updated at 02/01/2025: Продажи одного из товара были прекращены (PlatiMarket_sales_are_cancelled_2.png), из-за чего все 5 попыток были использованы
# Код исполняется нормально, как и ожидалось
# Посмотреть результат исполнения можно в 'Прогон_программы_5_PlatiMarket_Update_Items_с_перезапуском_парсера_02_01_2025_Все_использованные_попытки.txt'
# TODO: Сделать проверку для товаров, продажи которых были прекращены (Выполнено -> 20/01/2025)

# Может возникнуть проблема, поскольку должна быть запись в базе данных на момент доступности записи и на текущий момент продажи должны быть прекращены

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

    try:
        data_uuids, db_urls = getAllProductUrls(sql_cursor)
    except ValueError:
        print('Внимание: В базе данных не было обнаружено ни одной записи. '
              'Запустите скрипт парсинга \'PlatiMarket_Item_parser_v1.py\' для индивидуального добавления товара в базу...')

        return

    print('Данные url-адресов успешно получены...\n')
    print('Количество товаров в базе данных:', len(db_urls), end='\n')

    for (url_number, url), data_uuid in zip(enumerate(db_urls, start=1), data_uuids):

        print(f'\nЗагружаю страницу {url_number}, ожидайте....')

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
                # Updated at 02/02/2025: Применяю проверку заблокиран ли продавец на площадке PlatiMarket или нет

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

            product_name, product_price, product_sell_data, product_seller_name, product_seller_url, product_sell_count, product_refund_count, product_image_url = parserReload(url_number=url_number, url_str=url, tries=5)

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
