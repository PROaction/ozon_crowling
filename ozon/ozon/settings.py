BOT_NAME = "ozon"

SPIDER_MODULES = ["ozon.spiders"]
NEWSPIDER_MODULE = "ozon.spiders"

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
   "scrapy_selenium.SeleniumMiddleware": 800
   # раскомментировать если нужно прокси
    # 'rotating_proxies.middlewares.RotatingProxyMiddleware': 610,
    # 'rotating_proxies.middlewares.BanDetectionMiddleware': 620,
}
proxy_server_url = "3.127.203.145:80"
SELENIUM_DRIVER_ARGUMENTS = []
SELENIUM_DRIVER_NAME = 'chrome'
# Если нужен свой драйвер, то указать путь к нему
# SELENIUM_DRIVER_EXECUTABLE_PATH = "C:/path/to/your/file/chromedriver.exe"

USER_AGENT = ('Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 '
              '(KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36')


# раскомментировать если нужно прокси
# ROTATING_PROXY_LIST = [
#     '3.127.203.145:8888',
#     '3.127.203.145:8080',
#     '3.127.203.145:999',
#     '3.127.203.145:80',
#     '35.185.196.38:3128',
# ]

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   "ozon.pipelines.SmartphonePipeline": 1,
}

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

LOG_FILE = 'logfile.txt'
