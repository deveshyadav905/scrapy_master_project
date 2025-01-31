# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class PlantapiscraperItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    plant_id=scrapy.Field()
    sci_name=scrapy.Field()
    api_sci_name = scrapy.Field()
    images=scrapy.Field()

