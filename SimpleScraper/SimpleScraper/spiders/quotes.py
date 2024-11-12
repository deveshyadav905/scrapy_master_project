import scrapy

class QuotesSpider(scrapy.Spider):
    # Name of the spider, used to run the spider with "scrapy crawl quotes"
    name = "quotes"
    
    # Restrict the spider to only scrape this domain
    allowed_domains = ["quotes.toscrape.com"]
    
    # The starting URL for the spider; Scrapy will begin scraping from this page
    start_urls = ["http://quotes.toscrape.com"]

    def parse(self, response):
        # Extract the page's main title using XPath
        # (useful if you want to add a global attribute to each item)
        body_title = response.xpath("//div[@class='row header-box']//h1//text()").get()
        
        # Select all quote elements on the page, each one is inside a div with class "quote"
        row_items = response.xpath("//div[@class='row']//div[contains(@class,'quote')]")  
        
        # Loop through each quote item and extract relevant information
        for item in row_items:
            yield {
               
                'title': item.xpath(".//span[@class='text']/text()").get(),
                
                'author': item.xpath(".//span/small[@class='author']/text()").get(),
                
                'tag': ', '.join(item.xpath(".//div[@class='tags']//a/text()").getall())
            }
