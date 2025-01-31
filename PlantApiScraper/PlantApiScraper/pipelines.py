# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pymongo

class PlantapiscraperPipeline:
    def process_item(self, item, spider):
        return item


class MongoDBPipeline:
    def open_spider(self, spider):
        self.client = pymongo.MongoClient('mongodb://localhost:27017')
        self.db = self.client['Plants']
        self.collection = self.db['Plant_Images']

        # Ensure plant_id is indexed and unique
        self.collection.create_index([("plant_id", pymongo.ASCENDING)], unique=True)

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        try:
            # Insert or update the document to avoid duplicates
            self.collection.update_one(
                {"plant_id": item['plant_id']},  # Find by plant_id
                {"$set": dict(item)},  # Update the document
                upsert=True  # Insert if not exists
            )
        except pymongo.errors.DuplicateKeyError:
            spider.logger.warning(f"Duplicate entry skipped: {item['plant_id']}")
            return None  # Skip duplicate

        return item

    
    
    
# mongoexport --uri="mongodb://localhost:27017" --db=Plants --collection=Plant_Images --out=output.json
