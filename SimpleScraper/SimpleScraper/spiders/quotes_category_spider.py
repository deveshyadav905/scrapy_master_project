import scrapy

# TO RUN CRAWLING EXECUTE ONE OF THE FOLLOWING COMMANDS:
# 1. Run the spider and output to the console:
#    scrapy crawl categoryspider
#
# 2. Run the spider and save output to a JSON file:
#    scrapy crawl categoryspider -o categories.json
#
# 3. Run the spider and save output to a CSV file:
#    scrapy crawl categoryspider -o categories.csv

class CategorySpider(scrapy.Spider):
    name = "categoryspider"
    
    allowed_domains = ["quotes.toscrape.com"]
    start_urls = ["http://quotes.toscrape.com"]

    def parse(self, response):
        # Extract all category links from the homepage
        categories = response.xpath("//div[@class='col-md-4 tags-box']//a/@href").getall()
        # Loop through each category link and follow it
        for category in categories:
            category_url = response.urljoin(category)  # Construct full URL for the category
            yield scrapy.Request(category_url, callback=self.parse_category)

    def parse_category(self, response):
        # Now we're on a category page, let's scrape the quotes on this page
        row_items = response.xpath("//div[@class='row']//div[contains(@class,'quote')]")
        for item in row_items:
            quote_data = {
                'title': item.xpath(".//span[@class='text']/text()").get(),
                'author': item.xpath(".//span/small[@class='author']/text()").get(),
                'tags': ', '.join(item.xpath(".//div[@class='tags']//a/text()").getall())
            }
            yield quote_data

        # Handle pagination: Check if there's a next page
        next_page = response.xpath("//li[@class='next']/a/@href").get()
        if next_page:
            next_page_url = response.urljoin(next_page)  # Construct the full URL for the next page
            yield scrapy.Request(next_page_url, callback=self.parse_category)
