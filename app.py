import csv
import json
import scrapy
from scrapy.crawler import CrawlerProcess
from bs4 import BeautifulSoup as soup


items = []
BASE_URL = 'https://www.citilink.ru/catalog/mobile/smartfony/-moshhnye-smartfony?available=1&status=55395790&p=1'


class Product:
    """
    Product representation.
    """
    def __init__(self, product_obj):
        self.id = product_obj['id']
        self.price = product_obj['price']
        self.club_price = product_obj['clubPrice']
        self.brand = product_obj['brandName']
        self.name = product_obj['shortName']

    def __repr__(self):
        return 'ID: {0}, Brand: {1}, Name: {2}, Price: {3}, Club price {4} '.format(self.id, self.brand, self.name, self.price, self.club_price)

    def to_list(self):
        return [self.id, self.price, self.club_price, self.brand, self.name]


class PhonesSpider(scrapy.Spider):
    """
    Site crawler.
    """
    name = 'phones'
    start_urls = [
        BASE_URL
    ]

    def request(self, url, callback):
        """
        Wrapper for scrapy.request to set cookies.
        """
        request = scrapy.Request(url=url, callback=callback)
        request.cookies['new_design'] = 0
        request.headers['User-Agent'] = (
            'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, '
            'like Gecko) Chrome/45.0.2454.85 Safari/537.36')
        return request

    def get_next_page(self, page):
        """
        Get next page URL.
        """
        # Old UI
        next_page = page.find('li', {'class': 'next'})
        if next_page:
            href = next_page.find('a')
            return href['href']

        # New UI
        next_page = page.find('a', {'class': 'PaginationWidget__page_next'})
        if next_page:
            return next_page['href']

    def parse_items(self, page):
        """
        Parse product items on the page.
        """
        products = page.find_all('div', attrs={'data-product-id': True})

        for product in products:
            try:
                data_params = json.loads(product['data-params'])
                items.append(Product(data_params))
            except Exception as ex:
                print(ex)

    def parse(self, response):
        """
        Parse response.
        """
        page = soup(response.body, 'html.parser')
        self.parse_items(page)
        next_page = self.get_next_page(page)

        if next_page:
            yield scrapy.Request(next_page, callback=self.parse)


if __name__ == '__main__':
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36',
        'DEPTH_LIMIT': 10,
        'CLOSESPIDER_PAGECOUNT': 10,
    })

    process.crawl(PhonesSpider)
    process.start()

    for item in items:
        print(item)

    with open('result.csv', 'w') as csv_file:
        writer = csv.writer(csv_file, quoting=csv.QUOTE_ALL)
        for item in items:
            writer.writerow(item.to_list())
