import scrapy
import json
import csv
from PlantApiScraper.items import PlantapiscraperItem
from urllib import parse
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import random
import time

WEBSHARE_URL = {
    'WEBSHARE_URL_HTTP': 'http://znsyjsqi-rotate:2x2fhdxt4b79@p.webshare.io:80/',
}

class PlantsSpider(scrapy.Spider):
    name = "plants"
    allowed_domains = ["api.plantnet.org"]
    base_url = "https://api.plantnet.org/v1/projects/k-world-flora/species/autocomplete/{}?lang=en&page=0&pageSize=10&authorNames=true&includeSynonyms=true&includeCommonNames=true"
    
    def __init__(self, name=None, plant_list=None, **kwargs):
        super().__init__(name, **kwargs)
        self.plant_list = plant_list
        self.plant_data = {}  # Store plant details while waiting for all organs
        self.logger.setLevel('ERROR')
    def get_random_user_agent(self):
        """Generate a random User-Agent with Chrome version up to 131"""
        chrome_version = random.randint(100, 131)
        return f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_version}.0.0.0 Safari/537.36"

    def start_requests(self):
        headers = {'User-Agent': self.get_random_user_agent()}
        meta_options = {'proxy': WEBSHARE_URL["WEBSHARE_URL_HTTP"]}

        for plant in self.plant_list:
            plant_name = plant['sci_name']
            if 'var' in plant_name:
                plant_name = plant_name.split('var')[0].strip()
            elif 'f' in plant_name:
                plant_name = plant_name.split('f')[0].strip()

            encoded_plant_name = parse.quote(plant_name)
            url = self.base_url.format(encoded_plant_name)

            yield scrapy.Request(
                url=url,
                meta=meta_options,
                headers=headers,
                errback=self.handle_error,
                callback=self.parse_plant_details,
                cb_kwargs={'plant': plant}
            )

    def handle_error(self, failure):
        """Save failed plants to a JSON file"""
        plant = failure.request.cb_kwargs['plant']
        file_name = "not_found_plants.json"
        not_found_list = []

        try:
            with open(file_name, "r", encoding="utf-8") as f:
                not_found_list = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            not_found_list = []

        not_found_list.append(plant)

        with open(file_name, "w", encoding="utf-8") as f:
            json.dump(not_found_list, f, indent=4)

    def parse_plant_details(self, response, plant):
        plant_info = response.json()

        plant_id = plant.get('plant_id', '')
        sci_name = plant.get('sci_name', '')
        api_sci_name = next(
            (item['display'] for item in plant_info if item.get('level') == 'sp'), None
        )

        # Store plant data
        self.plant_data[plant_id] = {
            'plant_id': plant_id,
            'sci_name': sci_name,
            'api_sci_name': api_sci_name,
            'images': {}  # Will store images for each organ
        }

        # Fetch organ images (flower, leaf, bark, etc.)
        timestamp = int(time.time() * 1000)
        page_size = 20000
        organs = ["flower", "leaf", "bark", "habit", "other", "fruit"]
        if api_sci_name:
            for organ in organs:
                yield scrapy.Request(
                    url=f"https://api.plantnet.org/v1/projects/k-world-flora/species/{api_sci_name}/organs/{organ}?lang=en&maxDate={timestamp}&page=0&pageSize={page_size}",
                    callback=self.parse_organ_images,
                    meta={'plant_id': plant_id, 'organ': organ, 'total_organs': len(organs)}
                )

    def parse_organ_images(self, response):
        plant_id = response.meta['plant_id']
        organ = response.meta['organ']
        total_organs = response.meta['total_organs']
        image_data = response.json()

        # Store images for the organ
        image_urls = [item.get('o', item.get('m')) for item in image_data.get(organ, [])]
        self.plant_data[plant_id]['images'][organ] = image_urls

        # If all organs are collected, yield the final item
        if len(self.plant_data[plant_id]['images']) == total_organs:
            yield self.plant_data.pop(plant_id)  # Remove from memory and yield

if __name__ == "__main__":
    csv_path = "/home/charanjeet/projects/newsdatafeeds/ImageDATA.csv"

    with open(csv_path, newline='', encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        plant_list = list(reader)  # Read all rows into a list

    process = CrawlerProcess(get_project_settings())
    process.crawl(PlantsSpider, plant_list=plant_list)
    process.start()
