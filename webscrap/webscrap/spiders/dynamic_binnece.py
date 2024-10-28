import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import json
import pymongo

class BinanceglossarySpider(scrapy.Spider):
    name = "binanceglossary"
    
    # Limit the spider to only access URLs within this domain
    allowed_domains = ["academy.binance.com"]
    # Starting URL to scrape the Binance glossary data
    start_urls = ["https://academy.binance.com/en/glossary"]
    
    # Custom headers to make the request appear as if it is coming from a web browser
    headers = {
        'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
    }

    def __init__(self, *args, **kwargs):
        """Initialize MongoDB connection and set up collection for storing scraped data."""
        super(BinanceglossarySpider, self).__init__(*args, **kwargs)
        # Establish MongoDB connection
        self.client = pymongo.MongoClient("mongodb://localhost:27017/")
        self.db = self.client["binance_data"]
        self.collection = self.db["glossary"]

        # Create a unique index on the 'slug' field to prevent duplicate entries
        self.collection.create_index([("slug", pymongo.ASCENDING)], unique=True)
    
    def start_requests(self):
        """Send initial requests to the start URLs, with error handling."""
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse, headers=self.headers, errback=self.parse_error)
    
    def parse(self, response):
        """Extract data from the page, process it, and store it in MongoDB."""
        # Extract JSON data from the script tag with id="__APP_DATA"
        json_str_data = response.xpath('//script[@id="__APP_DATA"]//text()').get()
        
        if json_str_data:
            # Load JSON data as a dictionary
            json_dict_data = json.loads(json_str_data)
            
            # Navigate to the glossary items within the JSON structure
            glossary_items = json_dict_data.get('appState', {}).get('loader', {}).get('dataByRouteId', {}).get('02d6', {}).get('glossaries', [])

            for item in glossary_items:
                # Attempt to insert each item into MongoDB, handling duplicates
                try:
                    self.collection.insert_one(item)
                    self.logger.info(f"Inserted item: {item['title']}")
                except pymongo.errors.DuplicateKeyError:
                    # Skip items with duplicate 'slug' values
                    self.logger.info(f"Duplicate found, skipping item: {item['title']}")
        else:
            # Log error if the expected data is missing
            self.logger.error("No data found in script tag")
    
    def parse_error(self, failure):
        """Handle request errors by logging the status code."""
        response = failure.value.response
        if response:
            self.logger.error(f"Error occurred: status code {response.status}")

    def close(self, reason):
        """Close the MongoDB connection when the spider is done."""
        self.client.close()
        self.logger.info("MongoDB connection closed.")

if __name__ == "__main__":
    # Run the spider
    process = CrawlerProcess(get_project_settings())
    process.crawl(BinanceglossarySpider)
    process.start() 
