import scrapy

# TO RUN CRAWLING EXECUTE ONE OF THE FOLLOWING COMMANDS:
# 1. Run the spider and output to the console:
#    scrapy crawl multipagenavigator
# 
# 2. Run the spider and save output to a JSON file:
#    scrapy crawl multipagenavigator -o multipagenavigator.json
#
# 3. Run the spider and save output to a CSV file:
#    scrapy crawl multipagenavigator -o multipagenavigator.csv

class MultiPageNavigatorSpider(scrapy.Spider):
    name = "multipagenavigator"
    
    allowed_domains = ["quotes.toscrape.com"]
    start_urls = ["http://quotes.toscrape.com"]

    def parse(self, response):
                
        # Select each quote on the page
        row_items = response.xpath("//div[@class='row']//div[contains(@class,'quote')]")  
        
        # Loop through each quote and yield data
        for item in row_items:
            yield {
                'title': item.xpath(".//span[@class='text']/text()").get(),
                'author': item.xpath(".//span/small[@class='author']/text()").get(),
                'tag': ', '.join(item.xpath(".//div[@class='tags']//a/text()").getall())
            }
        
        # Find the link to the next page, if available
        next_page = response.xpath("//li[@class='next']/a/@href").get()
        
        # If a next page link is found, follow the link
        if next_page is not None:
            # response.follow constructs a full URL from a relative URL and follows it
            yield response.follow(next_page, callback=self.parse)