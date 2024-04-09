import re
import time

from scrapy_selenium import SeleniumRequest

import scrapy
from selenium.common import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from ozon.items import SmartphoneItem


class ScrapingClubSpider(scrapy.Spider):
    name = 'ozon_test'
    allowed_domains = ['ozon.ru']
    custom_settings = {
        'DOWNLOAD_DELAY': 2,
    }

    start_page = 1
    visited_urls = set()
    smartphone_count = 0
    smartphone_collected = 0
    operation_system_counter = dict()

    def start_requests(self):
        url = 'https://www.ozon.ru/category/telefony-i-smart-chasy-15501/?sorting=rating'
        yield SeleniumRequest(url=url, callback=self.parse_category, meta={'category_url': url})

    # def go_category_page(self, response, driver):
    #     self.start_page += 1
    #     next_page_url = f'https://www.ozon.ru/category/telefony-i-smart-chasy-15501/?page={self.start_page}&sorting=rating'
    #     self.logger.info('Переход на страницу с категориями:', next_page_url)
    #     driver.get(next_page_url)
    #     self.parse_category(response)

    def parse_category(self, response):
        self.logger.info("Начало работы parse_category")
        driver = response.request.meta["driver"]
        item = SmartphoneItem()

        # if self.smartphone_collected < 16:
        smartphone_elements = None
        self.logger.info('Поиск ссылок на смартфоны перед try.')
        try:
            self.logger.info('Поиск ссылок на смартфоны.')
            smartphone_elements = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, "//span[text()='Тип: ']/font[text()='Смартфон']/../../preceding-sibling::a"))
            )
        except TimeoutException:
            self.start_page += 1
            next_page_url = f'https://www.ozon.ru/category/telefony-i-smart-chasy-15501/?page={self.start_page}&sorting=rating'
            self.logger.info('Переход на страницу с категориями:', next_page_url)
            # driver.get(next_page_url)
            # self.parse_category(response)
            yield SeleniumRequest(url=next_page_url, callback=self.parse_category,  meta={'category_url': next_page_url})

        smartphone_urls = []
        if smartphone_elements:
            self.logger.info(f'Получаем ссылки на смартфоны на странице категории - {response.url}')
            self.logger.info(f'Объект smartphone_elements - {smartphone_elements}')
            smartphone_urls = [element.get_attribute('href').split('?asb2')[0] for element in smartphone_elements]
            self.logger.info(f'Получили {len(smartphone_urls)} ссылок на смартфоны на странице {self.start_page} - {smartphone_urls}')
        else:
            self.logger.info(f'На странице {self.start_page} не удалось найти элементы смартфоны. Переход на следующую страницу.')
            self.start_page += 1
            next_page_url = f'https://www.ozon.ru/category/telefony-i-smart-chasy-15501/?page={self.start_page}&sorting=rating'
            yield SeleniumRequest(url=next_page_url, callback=self.parse_category)


        for url in smartphone_urls:
            # if url not in self.visited_urls:
            if self.smartphone_collected < 25:
                self.logger.info(f"Переход на страницу смартфона: {url}")
                driver.get(url)
                #
                # self.parse_smartphone()
                # driver.back()
                # self.visited_urls.add(url)
                # yield SeleniumRequest(url=url, callback=self.parse_smartphone, meta={'url': url})
                self.logger.info(f'Поиск ОС смартфона - {url}')
                try:
                    item['operation_system'] = WebDriverWait(driver, 20).until(
                        EC.presence_of_all_elements_located(
                            (By.XPATH, "//dt/span[text()='Операционная система']/../following-sibling::dd/a"))
                    )[0].text
                except:
                    self.logger.warning(f'Не найдена ОС - {url}')

                self.logger.info(f"Нашли элемент operation_system - {item['operation_system']}")
                if item['operation_system'] == 'iOS':
                    self.logger.info('Поиск версии iOS.')
                    try:
                        item['operation_system_version'] = WebDriverWait(driver, 10).until(
                            EC.presence_of_all_elements_located(
                                (By.XPATH, "//dt/span[text()='Версия iOS']/../following-sibling::dd"))
                        )[0].text.split(' ')[1]
                    except:
                        self.logger.warning('Версия iOS не найдена.')
                        item['operation_system_version'] = 'None'
                    self.logger.info(f"Нашли элемент version - {item['operation_system_version']}")
                else:
                    self.logger.info('Поиск версии Android.')
                    try:
                        item['operation_system_version'] = WebDriverWait(driver, 10).until(
                            EC.presence_of_all_elements_located(
                                (By.XPATH, "//dt/span[text()='Версия Android']/../following-sibling::dd"))
                        )[0].text.split(' ')[1]
                    except:
                        try:
                            item['operation_system_version'] = WebDriverWait(driver, 10).until(
                                EC.presence_of_all_elements_located(
                                    (
                                    By.XPATH, '//span[contains(text(), "ОС") or contains(text(), "ОПЕРАЦИОННАЯ система")]'))
                            )[0].text
                            match = re.search(r"- ((?:\d|\w+\s\d+))(?:,|\s)", item['operation_system_version'])
                            if match:
                                print(match.group(1))
                                item['operation_system_version'] = match.group(1)
                                self.logger.info(f"Нашли элемент version - {item['operation_system_version']}")
                        except:
                            self.logger.warning('Версия Android не найдена.')
                            item['operation_system_version'] = 'None'
                    # except:
                    #     self.logger.warning('Версия Android не найдена.')
                    #     item['operation_system_version'] = 'None'


                self.smartphone_count += 1
                self.logger.info(f'Увеличили количество обработанных смартфонов = {self.smartphone_count}.')

                self.smartphone_collected += 1
                yield item

                # self.logger.info(f'Найдено смартфонов - {self.smartphone_collected}')
                # self.parse_smartphone(response)
                # driver.back()
            else:
                self.logger.info('Процесс завершен.')
                return
        else:
            self.logger.info(f'На странице {self.start_page} закончились смартфоны.')
            # self.go_category_page(response, driver)
            # current_page = int(re.search(r'page=(\d+)', self.driver.current_url).group(1))
            self.start_page += 1
            next_page_url = f'https://www.ozon.ru/category/telefony-i-smart-chasy-15501/?page={self.start_page}&sorting=rating'
            self.logger.info('Переход на страницу с категориями:', next_page_url)
            yield SeleniumRequest(url=next_page_url, callback=self.parse_category)

    def parse_smartphone(self, response):
        self.logger.info(f'Начало работы parse_smartphone - {response.url}')
        driver = response.request.meta["driver"]
        item = SmartphoneItem()

        # if self.smartphone_count >= 2:
        #     self.logger.info(f'Закрытие краулера.\nБыло найдено и обработано {self.smartphone_count} смартфонов.')
            # self.closed(self)
            # self.driver.quit()
            # self.crawler.engine.close_spider(self, 'smartphone_count_limit_reached')
            # raise scrapy.exceptions.CloseSpider('smartphone_count_limit_reached')
            # self.crawler.signals.send_catch_log(signal=signals.spider_closed, spider=self,
            #                                     reason='smartphone_count_limit_reached')
            # self.crawler.engine.stop()

        # driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # sleep(2)
        for x in range(0, 10):
            # scroll down by 10000 pixels
            ActionChains(driver) \
                .scroll_by_amount(0, 10000) \
                .perform()

            # waiting 2 seconds for the products to load
            time.sleep(1)

        self.logger.info(f'Поиск ОС смартфона - {response.url}')
        try:
            item['operation_system'] = WebDriverWait(driver, 20).until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, "//dt/span[text()='Операционная система']/../following-sibling::dd/a"))
            )[0].text
        except:
            self.logger.warning(f'Не найдена ОС - {response.url}')

        self.logger.info(f"Нашли элемент operation_system - {item['operation_system']}")
        if item['operation_system'] == 'iOS':
            self.logger.info('Поиск версии iOS.')
            try:
                item['operation_system_version'] = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located(
                        (By.XPATH, "//dt/span[text()='Версия iOS']/../following-sibling::dd"))
                )[0].text.split(' ')[1]
            except:
                self.logger.warning('Версия iOS не найдена.')
                item['operation_system_version'] = 'None'
            self.logger.info(f"Нашли элемент version - {item['operation_system_version']}")
        else:
            self.logger.info('Поиск версии Android.')
            try:
                item['operation_system_version'] = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located(
                        (By.XPATH, '//span[contains(text(), "ОС") or contains(text(), "ОПЕРАЦИОННАЯ система")]'))
                )[0].text
            except:
                self.logger.warning('Версия Android не найдена.')
                item['operation_system_version'] = 'None'
            match = re.search(r" --------------- (.*?),", item['operation_system_version'])
            if match:
                print(match.group(1))
                item['operation_system_version'] = match.group(1)
                self.logger.info(f"Нашли элемент version - {item['operation_system_version']}")

        # os = item['operation_system']
        # version = item['operation_system_version']
        # key = f'{os} - {version}'
        # if key in self.operation_system_counter:
        #     self.operation_system_counter[key] += 1
        # else:
        #     self.operation_system_counter[key] = 1

        self.smartphone_count += 1
        self.logger.info(f'Увеличили количество обработанных смартфонов = {self.smartphone_count}.')

        yield item

        # return self.operation_system_counter
        # return item
