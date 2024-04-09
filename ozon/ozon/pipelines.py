# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import json

from itemadapter import ItemAdapter


class SmartphonePipeline:
    results = dict()

    def open_spider(self, spider):
        print('open_spider')
        self.file = open('results.txt', 'w')

    def process_item(self, item, spider):
        print('process_item')
        # operation_system_counter = spider.crawler.stats.get_value('operation_system_counter')
        # for key, count in operation_system_counter.items():
        #     line = f"{key} — {count}\n"
        #     print(line)
        #     self.file.write(line)
        item = ItemAdapter(item)
        key = f'{item.get("operation_system")} {item.get("operation_system_version")}'
        if key in self.results:
            self.results[key] += 1
        else:
            self.results[key] = 1

        return item

    def close_spider(self, spider):
        print('close_spider')
        print(self.results)
        sorted_results = dict(sorted(self.results.items(), key=lambda x: x[1], reverse=True))
        print(sorted_results)
        for version, count in sorted_results.items():
            self.file.write(f'{version} - {count}\n')
        self.file.close()
