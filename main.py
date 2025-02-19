# Импорт BeautifulSoup - библиотеки для парсинга данных с web-страницы
from bs4 import BeautifulSoup
# Импорт Selenium - библиотеки для автоматизированого взаимодействия со страницей
from selenium import webdriver

# Импорт regexp для получения данных из строк с помощью регулярных выражений
import re

def main(*args):
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
    product_cell_count, product_refund_count = extracted_sell_data[:2]

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


    print('\nСпарсенное название товара:', product_name)
    print('Спарсенная цена товара:', product_price + ' руб.')
    print('Спарсенное имя продавца товара:', product_seller_name)
    print('Спарсенная ссылка на аккаунт продавца товара:', url_base + product_seller_url)

    print('Спарсенное количество проданого товара:', product_cell_count)
    print('Спарсенное количество возвратов товара:', product_refund_count)

    print('Спарсенная ссылка на изображение товара:', product_image_url)



if __name__ == '__main__':
    main()

