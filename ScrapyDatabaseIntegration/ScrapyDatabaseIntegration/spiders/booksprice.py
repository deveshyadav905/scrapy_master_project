import scrapy


class BookspriceSpider(scrapy.Spider):
    name = "booksprice"
    allowed_domains = ["booksprice.com"]
    start_urls = ["https://booksprice.com"]

    def parse(self, response):
        pass
