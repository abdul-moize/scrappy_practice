import scrapy


class ExampleSpider(scrapy.Spider):
    name = 'example'
    allowed_domains = ['exmaple.com']
    start_urls = ['http://exmaple.com/']

    def parse(self, response):
        pass
