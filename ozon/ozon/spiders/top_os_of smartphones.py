import re
import time

import scrapy
from scrapy_selenium import SeleniumRequest
from selenium.common import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from ozon.items import SmartphoneItem


SMARTPHONE_COUNT = 20
WAIT_TIME = 5
SCROLL_COUNT = 3
SCROLL_PIXELS = 1000


class ScrapingClubSpider(scrapy.Spider):
    name = 'top_os_of_smartphones'
    allowed_domains = ['ozon.ru']
    custom_settings = {
        'DOWNLOAD_DELAY': 2,
    }

    start_page = 1
    visited_urls = set()
    smartphone_collected = 0
    operation_system_counter = dict()

    def start_requests(self):
        url = 'https://www.ozon.ru/category/telefony-i-smart-chasy-15501/?sorting=rating'
        yield SeleniumRequest(url=url, callback=self.parse_category, meta={'category_url': url})

    def parse_category(self, response):
        self.logger.info('Начало работы parse_category')
        driver = response.request.meta['driver']
        item = SmartphoneItem()

        smartphone_elements = None
        try:
            self.logger.info('Поиск ссылок на смартфоны.')
            smartphone_elements = WebDriverWait(driver, WAIT_TIME).until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, '//span[text()="Тип: "]/font[text()="Смартфон"]/../../preceding-sibling::a'))
            )
        except TimeoutException:
            self.logger.info(f'На странице {self.start_page} нет смартфонов.')
            self.start_page += 1
            next_page_url = (f'https://www.ozon.ru/category/telefony-i-smart-chasy-15501/'
                             f'?page={self.start_page}&sorting=rating')
            self.logger.info('Переход на страницу с категориями:', next_page_url)
            yield SeleniumRequest(url=next_page_url, callback=self.parse_category, priority=-self.start_page)

        smartphone_urls = [element.get_attribute('href').split('?asb2')[0] for element in smartphone_elements]
        self.logger.info(f'Получили {len(smartphone_urls)} ссылок на смартфоны на странице '
                         f'{self.start_page} - {smartphone_urls}')

        for i, url in enumerate(smartphone_urls):
            if url not in self.visited_urls:
                if self.smartphone_collected < SMARTPHONE_COUNT:
                    self.logger.info(f'Переход на страницу смартфона: {url}')
                    driver.get(url)
                    self.visited_urls.add(url)

                    self.logger.info(f'Поиск ОС смартфона - {url}')
                    try:
                        item['operation_system'] = WebDriverWait(driver, WAIT_TIME).until(
                            EC.presence_of_all_elements_located(
                                (By.XPATH, ('//dt/span[text()="Операционная система"]/../following-sibling::dd/a '
                                            '| //dt/span[text()="Операционная система"]/../following-sibling::dd')
                                 )
                            )
                        )[0].text
                    except:
                        self.logger.warning(f'Не найдена ОС из-за таймаута - {url}')

                    self.logger.info(f'Нашли элемент operation_system - {item["operation_system"]}')
                    if item['operation_system'] == 'iOS':
                        self.logger.info('Поиск версии iOS.')
                        try:
                            item['operation_system_version'] = WebDriverWait(driver, WAIT_TIME).until(
                                EC.presence_of_all_elements_located(
                                    (
                                        By.XPATH,
                                        '//div[@id="section-characteristics"]'
                                        '//dt/span[text()="Версия iOS"]/../following-sibling::dd')
                                )
                            )[0].text.split(' ')[1]
                        except:
                            self.logger.warning(f'Версия iOS не найдена - {url}')
                            item['operation_system_version'] = 'без версии'
                        self.logger.info(f'Нашли элемент version - {item["operation_system_version"]}')
                    else:
                        self.logger.info('Поиск версии Android.')

                        # скролл стринцы со смартфоном.
                        for x in range(0, SCROLL_COUNT):
                            ActionChains(driver) \
                                .scroll_by_amount(0, SCROLL_PIXELS) \
                                .perform()

                            time.sleep(1)
                        try:
                            item['operation_system_version'] = WebDriverWait(driver, WAIT_TIME).until(
                                EC.presence_of_all_elements_located(
                                    (By.XPATH, '//dt/span[text()="Версия Android""]/../following-sibling::dd'))
                            )[0].text.split(' ')[1]
                        except:
                            try:
                                item['operation_system_version'] = WebDriverWait(driver, WAIT_TIME).until(
                                    EC.presence_of_all_elements_located(
                                        (
                                            By.XPATH,
                                            ('//div[@id="section-description"]//span[contains(text(), "ОС") or '
                                             'contains(text(), "ОПЕРАЦИОННАЯ система") or '
                                             'contains(text(), "OS")]')
                                        )
                                    )
                                )[0].text
                                self.logger.info(f'Нашли текст версии Android в описании - '
                                                 f'{item["operation_system_version"]}')
                                match = re.search(
                                    r'(?:-|:)\s*([\w\s\d\.]*)(?:,|\s|$)',
                                    item['operation_system_version']
                                )
                                if match:
                                    item['operation_system_version'] = match.group(1)
                                    self.logger.info(f'Нашли элемент version - {item["operation_system_version"]}')
                                else:
                                    self.logger.warning(f'Версия Android не найдена - {url}\n {match}')
                                    item['operation_system_version'] = 'без версии'

                            except:
                                self.logger.warning(f'Версия Android не найдена  - {url}')
                                item['operation_system_version'] = 'без версии'

                    self.smartphone_collected += 1
                    self.logger.info(f'Увеличили количество обработанных смартфонов = {self.smartphone_collected}.')

                    yield item
                else:
                    self.logger.info('Процесс завершен.')
                    self.crawler.engine.close_spider(self, f'Собрано {self.smartphone_collected} смартфонов')
                    return
        else:
            self.logger.info(f'На странице {self.start_page} закончились смартфоны.')
            self.start_page += 1
            next_page_url = (f'https://www.ozon.ru/category/telefony-i-smart-chasy-15501/'
                             f'?page={self.start_page}&sorting=rating')
            self.logger.info('Переход на страницу с категориями:', next_page_url)
            yield SeleniumRequest(url=next_page_url, callback=self.parse_category, priority=-self.start_page)
