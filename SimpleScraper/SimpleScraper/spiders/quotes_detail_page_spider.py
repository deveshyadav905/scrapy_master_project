import scrapy

# TO RUN CRAWLING EXECUTE ONE OF THE FOLLOWING COMMANDS:
# 1. Run the spider and output to the console:
#    scrapy crawl detailpagespider
#
# 2. Run the spider and save output to a JSON file:
#    scrapy crawl detailpagespider -o details.json
#
# 3. Run the spider and save output to a CSV file:
#    scrapy crawl detailpagespider -o details.csv

# Disable duplicate filtering to allow all quotes to be saved in Settings
    # DUPEFILTER_CLASS = 'scrapy.dupefilters.BaseDupeFilter'

class DetailPageSpider(scrapy.Spider):
    name = "detailpagespider"
    
    # Define the allowed domains and the starting URLs
    allowed_domains = ["quotes.toscrape.com"]
    start_urls = ["http://quotes.toscrape.com"]

    def parse(self, response):
        """
        Parse the main page and extract the quote details.
        This function also handles pagination and follows the next page links.
        """
        # Select each quote element on the current page
        row_items = response.xpath("//div[@class='row']//div[contains(@class,'quote')]")
        
        # Loop through each quote on the page
        for item in row_items:
            # Scrape quote details like title, author, and tags
            quote_data = {
                'title': item.xpath(".//span[@class='text']/text()").get(),
                'author': item.xpath(".//span/small[@class='author']/text()").get(),
                'tags': ', '.join(item.xpath(".//div[@class='tags']//a/text()").getall())
            }
            
            # Extract the link to the author's detail page
            author_link = item.xpath(".//span/a/@href").get()
            
            # If the author's link is available, follow it to scrape additional author details
            if author_link is not None:
                yield response.follow(
                    author_link,  # Follow the link to the author's detail page
                    callback=self.parse_author,  # Callback to handle author details
                    meta={'quote_data': quote_data}  # Pass quote data to the next callback
                )

        # Find and follow the link to the next page, if it exists
        next_page = response.xpath("//li[@class='next']/a/@href").get()
        if next_page:
            # Log the next page URL for debugging
            self.logger.error(f"Following next page {next_page}")
            yield response.follow(next_page, callback=self.parse)

    def parse_author(self, response):
        """
        Parse the author's page and extract additional details like birth date, birth place, and description.
        Combine author details with the quote data and return the complete data.
        """
        # Retrieve the passed quote data from the previous page
        quote_data = response.meta['quote_data']
        
        # Extract additional author details
        author_details = {
            'birth_date': response.xpath("//span[@class='author-born-date']/text()").get(),
            'birth_place': response.xpath("//span[@class='author-born-location']/text()").get(),
            'description': response.xpath("//div[@class='author-description']/text()").get().strip()
        }
        
        # Combine the quote data with the author's details and yield the complete item
        yield {**quote_data, **author_details}
