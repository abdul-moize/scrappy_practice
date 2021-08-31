import json

import scrapy
from functools import partial


class PakistanStoresSpider(scrapy.Spider):
    """
    This class crawls the site pakistanistores.com and extracts data
    """
    name = "pakistan_stores"
    start_urls = [
        'https://pakistanistores.com/prices/home-appliances/led-tv-prices',
    ]
    current_page = 1
    products = []
    processed_products = 0

    def parse(self, response):
        """
        This function crawls through each page and extracts all product information
        Args:
            response(TextReponse): Contains the page contents
        Returns:
            (Any or None):  A request to another page
                            Or
                            None if everything processed
        """
        last_page = response.css('a.page-link.navigate::attr(data-href)')[-1].get()
        last_page_number = int(last_page[last_page.find("=") + 1:])
        if self.current_page <= last_page_number:
            next_page_url = response.urljoin(f"?page={self.current_page}")
            yield scrapy.Request(url=next_page_url, callback=self.parse)
            product_containers = response.css('li.col-md-3.col-md-3.col-sm-6.col-xs-6 a')
            for product_container in product_containers:
                name = product_container.attrib['title']
                url = response.urljoin(product_container.attrib['href'])
                img_url = product_container.css('img.lazyload').attrib['data-src']
                price = product_container.css('div.primary-color.price::text').get()[0:-1]
                product = {
                    'name': name,
                    'link': url,
                    'img_link': response.urljoin(img_url),
                    'price': price
                }
                self.products.append(product)
            self.current_page += 1
        else:
            for product in self.products:
                link = product['link']
                binded_f = partial(self.extract_description, product)
                product['description'] = ""
                if link.__contains__('/product/'):
                    self.increment_and_check()
                else:
                    yield scrapy.Request(url=link, callback=binded_f)

    def extract_description(self, product, response):
        """
        This function extracts description of the product from the response
        Args:
            product(dict):  Dictionary containing product information
                            like, name, link, img_link and price
            response(TextResponse): Response object containing page contents
        Returns:
            None
        """
        index = self.products.index(product)
        description = response.css('div.light p::text')[-1].get()[1:-1]
        product['description'] = description
        self.products[index] = product
        self.increment_and_check()

    def write_to_file(self):
        """
        This function writes the jsonArray self.products to the file products.json
        Returns:
            None
        """
        json.dump(self.products, open('products.json', "w"), indent=4)

    def increment_and_check(self):
        """
        Checks if all the products are processed or not
        Returns:
            None
        """
        self.processed_products += 1
        if self.processed_products >= len(self.products):
            self.write_to_file()
