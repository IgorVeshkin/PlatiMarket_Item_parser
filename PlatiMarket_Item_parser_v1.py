# Данный файл предназначен для добавления новой записи товара в базу данных. Если запись уже в базе данных,
# то актуализирую данные и вывожу актуальные данные по записи

# Импорт BeautifulSoup - библиотеки для парсинга данных с web-страницы
from bs4 import BeautifulSoup
# Импорт Selenium - библиотеки для автоматизированого взаимодействия со страницей
from selenium import webdriver

# Импорт regexp для получения данных из строк с помощью регулярных выражений
import re

# Импорт для проверки наличия файла базы данных
import os

# Импорт функции создания базы данных, построения связи и закрытия связи. Своя функция
from DatabaseOperation.databaseBasicOperations import createDatabase, buildSqlConnection, closeSqlConnection

# Импорт функции проверки наличия записи в базе и создания записи базы данных. Своя функция
from DatabaseOperation.databaseInteractionOperations import checkRecord, createRecord, updateRecordData, getRecordUpdatableData

def main():
    # Основа ссылки, ведущая на сайт Plati Market
    url_base = 'https://plati.market/'

    print('Пример ссылки: itm/resident-evil-4-deluxe-remake-kljuch-xbox-series/4654421\n')

    while True:
        # Ввод ссылки на товар на Plati Market
        url = input('Введите ссылку на товар на Plati Market: ')

        # Если в переменную ссылки не было передано текста вообще
        # или переданна только неопределенная последовательность пробелов
        if not url or url.strip() == '':
            print(
                '\nВнимание: Вы не передали ссылку товара площадки Plati Market. Будет использована ссылка из примера\n')

            url = 'itm/resident-evil-4-deluxe-remake-kljuch-xbox-series/4654421'

        # Если в ссылке присутствуют пустые строки, то я их удаляю
        if ' ' in url:
            print('\nВ ссылку обнаружены пустые строки, они были успешно удалены \n')
            url = url.replace(" ", "")

        # Если первый элемент переданной ссылки является '/', то удаляем его
        if url[0] == '/':
            url = url[1:]
            print('\nВ ссылку первым элементов выступает \'/\', он был успешно удален \n')

        break


    # Формирую полноценную ссылку
    url = url_base + url

    print('Ваша ссылка:', url, end='\n\n')

    print('Загружаю страницу, ожидайте....')

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
                    f'\nПоскольку продажи товара \'{product_name}\' были прекращены, получить актуальные данные невозможно. Прекращаю работу парсера...')

                return

            # Конец блока проверки заблокированного пользователя

            print('\nВнимание:', buying_form.h1.text.strip().split("\n")[0])
            print(
                f'\nПоскольку продажи товара \'{product_name}\' были прекращены, получить актуальные данные невозможно. Прекращаю работу парсера...')
            return

        # Пример ссылки: itm/resident-evil-revelations-2-deluxe-steam-gift/3115261 (товар закончился на момент 20/01/2025)
        elif 'Этот товар закончился' in str(buying_form):
            print('\nВнимание:', buying_form.h1.text.strip().split("\n")[0])
            print(
                f'\nПоскольку товар \'{product_name}\' закончился, получить актуальные данные невозможно. Прекращаю работу парсера...')
            return

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

        # Имя продавца
        product_seller_url = url_base + product_seller_url

    except AttributeError:
        print('\nВнимание: элемент содержащий данные не был найден. Возможно сайт начал блокировать парсер...')
        print('\nПопробуйте запустить парсер позже...')
        return

    # Вывод спарсенных данных товара в терминал
    print('\nСпарсенное название товара:', product_name)
    print('Спарсенная цена товара:', product_price + ' руб.')
    print('Спарсенное имя продавца товара:', product_seller_name)
    print('Спарсенная ссылка на аккаунт продавца товара:', product_seller_url)

    print('Спарсенное количество проданого товара:', product_sell_count)
    print('Спарсенное количество возвратов товара:', product_refund_count)

    print('Спарсенная ссылка на изображение товара:', product_image_url)


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

    # Раздел взаимодействия с базой данных

    # Название и/или путь до файла базы данных
    my_database_path = 'PlatiMarket_db.db'

    # Если база данных по указанному пути не найдена
    if not os.path.isfile(my_database_path):
        # Создаю базу данных определенной структуры
        sql_connection, sql_cursor = createDatabase(db_name=my_database_path)
    else:
        # Если база существует, просто формируем подключение
        sql_connection, sql_cursor = buildSqlConnection(db_name=my_database_path)

    data_uuid = checkRecord(sql_cursor, data=parsed_data)

    if data_uuid:
        print('\nЗапись данного товара была найдена...\n')
        print('Произвожу проверку актуальности данных...\n')

        # TODO: Разработать функционал внесения актуальных данных: записи новой цены, количества проданых товаров и возвратов (Выполнено)
        # TODO: Осталось сделать обновление количества проданых товаров и возвратов (Выполнено)

        updateRecordData(sql_connection, sql_cursor, parsed_data, data_id=data_uuid)

        getRecordUpdatableData(sql_cursor, data_uuid)

        # TODO: Отредактировать структуру данных базы данных. Перенести soldCount и refundCount из Item_Data в Item_Price (Выполнено)
        # TODO: Переименновать Item_Price в Updatable_Data (Выполнено)

        # Закрываю соединение
        closeSqlConnection(sqlite_connection=sql_connection)

    else:
        print('\nДанные о товаре не были найдены...\n')
        print('Создаю запись...')

        # Создаю новую запись
        createRecord(sql_connection, sql_cursor, parsed_data)

        # Закрываю соединение
        closeSqlConnection(sqlite_connection=sql_connection)


if __name__ == '__main__':
    main()

