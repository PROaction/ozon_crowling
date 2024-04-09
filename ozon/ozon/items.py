# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import Item, Field


class SmartphoneItem(Item):
    operation_system = Field()
    operation_system_version = Field()
