# Краулер сайта Ozon.ru
Краулер, состоящий из одного паука, собирающего информацию об ОС смартфонов на сайте ozon.ru.
## Функционал:
1. Собирает информацию об операционных системах смартфонов со страницы "Телефоны и смарт-часы" 
(https://www.ozon.ru/category/telefony-i-smart-chasy-15501/).
2. Группирует полученные данные по операционной системы и ее версии.
3. Записывает результаты в файл results.txt в виде списка по убыванию.

Пример:
```angular2html
iOS 15 - 28
iOS 17 - 19
Android 13.x - 13
iOS 16 - 11
Android 12.x - 6
Android 13 - 4
Android без версии - 4
Android MIUI 14 - 3
iOS 14 - 3
Android MIUI 14 для POCO - 2
Android Работает на базе Xiaomi HyperOS11 - 2
Android Глобальная версия - 2
iOS без версии - 1
Android 11.x - 1
Android 14 - 1

```
<!--Установка-->
## Установка
1. Клонировать репозиторий
```git@github.com:PROaction/ozon_crowling.git```
2. Установить Poetry, если не установлен
3. Активировать виртуальное окружение
``` poetry shell```
4. Установить зависимости
``` poetry install --no-root```
5. Найти, где расположена библиотека scrapy-selenium
``` pip show scrapy-selenium```
6. Заменить содержимое файла middlewares.py в библиотеки, на middlewares.py, что в корне проекта
7. Перейти в директорию ozon
``` cd .\ozon\```
8. Запустить паука
```scrapy crawl top_os_of_smartphones```

<!--Пользовательская документация-->
## Документация
Исполнемый файл - top_os_of smartphones.py. В файле есть ряд констант, котоые позволяет изменять поведение паука:\
SMARTPHONE_COUNT - количество смартфонов, информацию по которым нужно собрать\
WAIT_TIME - секунды ожидания каждого элемента на странице\
SCROLL_COUNT - количество скролов на странице смартфона для получения элементов страницы (ОС и версия)\
SCROLL_PIXELS - длина одного скрола