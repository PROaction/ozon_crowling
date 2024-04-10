from itemadapter import ItemAdapter
import pandas as pd


class SmartphonePipeline:
    def __init__(self):
        self.data = []

    def open_spider(self, spider):
        self.file = open('results.txt', 'w')

    def process_item(self, item, spider):
        item = ItemAdapter(item)
        self.data.append({
            'operation_system': item.get("operation_system"),
            'operation_system_version': item.get("operation_system_version")
        })
        return item

    def close_spider(self, spider):
        df = pd.DataFrame(self.data)
        df['key'] = df['operation_system'] + ' ' + df['operation_system_version']
        result = df['key'].value_counts().reset_index()
        result.columns = ['version', 'count']
        for index, row in result.iterrows():
            self.file.write(f'{row["version"]} - {row["count"]}\n')
        self.file.close()
