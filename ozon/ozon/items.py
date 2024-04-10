from scrapy.item import Field, Item


class SmartphoneItem(Item):
    operation_system = Field()
    operation_system_version = Field()
