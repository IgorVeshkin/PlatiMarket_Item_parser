# Проект парсинга и хранения данных товаров с площадки PlatiMarket

## Описание
В рамках проекта был реализован функционал парсинга данных цифровых товаров площадки PlatiMarket. Полученные данные хранятся в базе данных определенной структуры, что позволяет производить определенные манипуляции с ними: хранение, удаление, обновление, а также взаимодействие для формирования статистики

## Основные технологии проекта
Язык программирования: `Python 3.12`

Проект был разработан с использованием библиотек `BeautifulSoup4`, `Selenium` и стандартной (встроенной в `Python`) библиотеки `Sqlite3`

## Установка проекта
Выполните команду `pip install -r requirements.txt` для установки всех зависимойстей проекта в виртуальную среду

## Структура проекта
``` commandline 
│   main.py
│   PlatiMarket Item Parser - Basic Project DataBase Structure.drawio
│   PlatiMarket_Database_Migrate_Data.py
│   PlatiMarket_db.db
│   PlatiMarket_db_Backup.db
│   PlatiMarket_Delete_Item.py
│   PlatiMarket_Get_All_Seller_Products.py
│   PlatiMarket_Get_SalesData_by_Month_and_Year.py
│   PlatiMarket_Get_Updatable_Data.py
│   PlatiMarket_Item_parser_v1.py
│   PlatiMarket_Update_Items.py
│   PlatiMarket_Update_Offsetted_Items.py
│   README.md
│   requirements.txt
│   SQL_Playground.py
│
├───Scripts_Results
│       Выполнение скрипта PlatiMarket_Update_Items 05.02.2025.txt
│       Выполнение скрипта PlatiMarket_Update_Items 06.02.2025.txt
│       Пример прогона скрипта PlatiMarket_Updated_Offsetted_Items, в котором один из продавцов заблокирован.txt
│       Прогон_программы_2_PlatiMarket_Update_Items_с_перезапуском_парсера_31_12_2024.txt
│       Прогон_программы_3_PlatiMarket_Update_Items_с_перезапуском_парсера_31_12_2024.txt
│       Прогон_программы_4_PlatiMarket_Update_Items_с_перезапуском_парсера_02_01_2025.txt
│       Прогон_программы_5_PlatiMarket_Update_Items_с_перезапуском_парсера_02_01_2025_Все_использованные_попытки.txt
│       Прогон_программы_PlatiMarket_Update_Items_с_перезапуском_парсера_31_12_2024.txt
│
├───databaseDrafts
│       database.db
│       databaseCreate.py
│       DatabaseInsert.py
│       DatabaseUpdate.py
│
├───DatabaseOperation
│       databaseBasicOperations.py
│       databaseInteractionOperations.py
│
└───Stop Selling Item Data Base (Forza Horizon 4)
        PlatiMarket_db.db
        Вывод скрипта PlatiMarket_Update_Items с базой данных, у которой продажи одного из товаров были прекращены.txt
```

## Основные скрипты

Всего проект состоит из 9 скриптов, предназначенных прямого взаимодействия с пользователем

__PlatiMarket_Item_parser_v1.py__ </br>
- __Описание:__ Скрипт используется для добавления нового товара в базу данных;
- __Дополнительный функционал:__ Создание базы данных определенной целями проекта структуры (Если в дериктории со скриптом отсутствует файл `PlatiMarket_db.db`, то он будет создан).

__PlatiMarket_Update_Items.py__ </br>
- __Описание:__ Скрипт используется для актуализации обновляемой информации товаров. Берутся все товары хранящиеся в базе данных и производится парсинг актуальных данных;
- __Дополнительный функционал:__ Создание базы данных определенной целями проекта структуры (Если в дериктории со скриптом отсутствует файл `PlatiMarket_db.db`, то он будет создан).

__PlatiMarket_Update_Offsetted_Items.py__ </br>
- __Описание:__ Функционал скрипта аналогичен `PlatiMarket_Update_Items.py` за исключением того, что перед запуском актуализации данных, необходимо будет ввести номер товара, с которого будет начат процесс;
- __Дополнительный функционал:__ Создание базы данных определенной целями проекта структуры (Если в дериктории со скриптом отсутствует файл `PlatiMarket_db.db`, то он будет создан).

__PlatiMarket_Delete_Item.py__ </br>
- __Описание:__ Скрипт производит удаление определенной записи товара из базы данных, а также сопутствующих связанных записей: `url-адреса`, `обновляемых данных`, `продавца` (если больше товаров у него нет);
- __Дополнительный функционал:__ Создание базы данных определенной целями проекта структуры (Если в дериктории со скриптом отсутствует файл `PlatiMarket_db.db`, то он будет создан).

__PlatiMarket_Get_Updatable_Data.py__ </br>
- __Описание:__ Скрипт выводит все обновляемые данные для каждого товара в базе. Вывод аналогичен выводу скриптов `PlatiMarket_Update_Items.py` и `PlatiMarket_Update_Offsetted_Items.py` за исключение того, что не производится запуск парсера актуализации данных.

__PlatiMarket_Database_Migrate_Data.py__ </br>
- __Описание:__ Скрипт производит миграцию данных из backup-базы данных `PlatiMarket_db_Backup.db` в актуальную  `PlatiMarket_db.db` (для работы должны присутствовать обе базы в дериктории скрипта).

__PlatiMarket_Get_All_Seller_Products.py__ </br>
- __Описание:__ Скрипт отборажает все продукты/товары, связанные с определенным продавцом.

__PlatiMarket_Get_SalesData_by_Month_and_Year.py__ </br>
- __Описание:__ Скрипт выводит количество проданных копий товара на площадке за весь месяц. Вывод производится для все товаров базы данных в формате месяц/год.

__SQL_Playground.py__ </br>
- __Описание:__ Скрипт выступает в роли испытательного полегона `sql-запросов`, которые будет применяться в скриптах проекта.


## Пакет взаимодействия с базой данных

Организация работы основных скриптов с базой данных реализуется с помощью самописного python-пакета `DatabaseOperation`.

Пакет состоит из 2 файлов `databaseBaseOperations.py` и `databaseInteractionOperations.py`

__databaseBaseOperations.py__ </br>
- __Описание:__ В данном скрипте прописан основной функционал взаимодействия с базой данных:
  1. создание файла базы данных определенной структуры (описанна в `py-файле`);
  2. подключение к базе данных и создание устойчивого подключения; 
  3. закрытие текущего соединения с базой.  

__databaseInteractionOperations.py__ </br>
- __Описание:__ В данном скрипте находятся функции производящие взаимодействие и манипуляции с данными базы данных


## Сторонние файлы

__main.py__ </br>
- __Описание:__ В файле хранится код раннего функционала парсера  

__PlatiMarket Item Parser - Basic Project DataBase Structure.drawio__ </br>
- __Описание:__ Структура базы данных, сделанная и описанная в сервисе draw.io

__databaseDrafts__ </br>
- __Описание:__ В директории хранятся `py-файлы`, описывающие прототип базы данных

__Scripts_Results__</br>
- __Описание:__ Директория, которая хранит в себе результат выполнения тех или иных основных скриптов в формате `.txt`

__Stop Selling Item Data Base (Forza Horizon 4)__
- __Описание:__ Директория с базой данных, в которой у одного товара были полностью прекращены продажи (для примера)

## Миграция базы данных 

При внесении изменений в структуру базы данных (добавление поля, триггера или таблицы), выполните следующий алгоритм действий:

1. Переименуйте текущую базу данных `PlatiMarket_db.db` на `PlatiMarket_db_Backup.db`;
2. Создайте новую чистую базу данных с корректировками в структуре, выполнив один из основных скриптов с дополнительным функционалом: например, `PlatiMarket_Item_parser_v1.py`;
3. Выполните скрипт `PlatiMarket_Database_Migrate_Data.py`, чтобы перенести данные.

Данный алгоритм позволит перенести данные backup базы данных в базу актуальной структуры.