import json
from bs4 import BeautifulSoup as soup
from urllib.request import urlopen


# BASE_URL = 'https://www.citilink.ru/catalog/mobile/smartfony/-moshhnye-smartfony/'
BASE_URL = 'https://www.citilink.ru/catalog/mobile/smartfony/-moshhnye-smartfony?available=1&status=55395790&p=3'


class Product:
    def __init__(self, product_obj):
        self.id = product_obj['id']
        self.price = product_obj['price']
        self.club_price = product_obj['clubPrice']
        self.brand = product_obj['brandName']
        self.name = product_obj['shortName']

    def __repr__(self):
        return 'ID: {0}, Brand: {1}, Name: {2}, Price: {3}, Club price {4} '.format(self.id, self.brand, self.name, self.price, self.club_price)


def parse_site():
    with urlopen(BASE_URL) as page:
        page = soup(page.read(), 'html.parser')
        products_list = page.find('div', {'class': 'product_category_list'})
        products = products_list.find_all('div', attrs={'data-product-id': True})

        items = []

        for product in products:
            data_params = json.loads(product['data-params'])
            items.append(Product(data_params))

        for item in items:
            print(item)


if __name__ == '__main__':
    parse_site()
