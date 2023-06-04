"""
This module contains a spider of pakistanistores.com site
that crawls and extracts data
"""
from functools import partial

import scrapy

from ..constants import TEXT_PROP
from ..utils import write_to_file


class PakistanStoresSpider(scrapy.Spider):
    """
    This class crawls the site pakistanistores.com and extracts data
    """

    name = "pakistan_stores"
    current_page = 1
    products = []
    processed_products = 0

    def start_requests(self):
        url = getattr(self, "url", None)
        yield scrapy.Request(url, self.parse)

    def parse(self, response, **kwargs):
        """
        This function crawls through each page and extracts all product information
        Args:
            response(TextReponse): Contains the page contents
        Returns:
            (Any or None):  A request to another page
                            Or
                            None if everything processed
        """
        last_page = response.css("a.page-link.navigate")[-1].attrib["data-href"]
        last_page_number = int(last_page[last_page.find("=") + 1 :])
        product_containers = response.css("li.col-md-3.col-md-3.col-sm-6.col-xs-6 a")
        for product_container in product_containers:
            name = product_container.attrib["title"]
            page_url = response.urljoin(product_container.attrib["href"])
            img_url = product_container.css("img.lazyload").attrib["data-src"]
            price = product_container.css(f"div.primary-color.price{TEXT_PROP}").get()[
                :-1
            ]
            product = {
                "name": name,
                "product_link": page_url,
                "img_link": response.urljoin(img_url),
                "price": price,
            }
            self.products.append(product)
        self.current_page += 1
        if self.current_page <= last_page_number:
            next_page_url = response.urljoin(f"?page={self.current_page}")
            yield scrapy.Request(url=next_page_url, callback=self.parse)
        else:
            for product in self.products:
                link = product["product_link"]
                extract_product_description = partial(self.extract_description, product)
                product["description"] = ""
                if link.__contains__("/product/"):
                    self.increment_and_check()
                else:
                    yield scrapy.Request(url=link, callback=extract_product_description)

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
        description = response.css(f"div.light p{TEXT_PROP}")[-1].get()[1:-1]
        product["description"] = description
        self.products[index] = product
        self.increment_and_check()

    def increment_and_check(self):
        """
        Checks if all the products are processed or not
        Returns:
            None
        """
        self.processed_products += 1
        if self.processed_products >= len(self.products):
            write_to_file(self.products)
