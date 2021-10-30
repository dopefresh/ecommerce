from bs4 import BeautifulSoup

import os
import re
import json
from loguru import logger


def find_max_number(text):
    result = [e for e in re.split("[^0-9]", text) if e != '']
    return max(map(int, result))


files = [f for f in os.listdir('documents')]

parsed_data = []
for file_name in files:
    logger.info(file_name)
    content = open(os.path.join('documents', file_name), 'r', encoding='utf-8')

    soup = BeautifulSoup(content, features="html.parser")
    for div in soup.findAll('div', attrs={'class': 'catalog-product ui-button-widget'}):
        name = div.find('a', attrs={'class': 'catalog-product__name ui-link ui-link_black'})\
            .find('span')\
            .contents[0]

        image = div.find('div', attrs={'class': 'catalog-product__image'})
        image_href = ''
        try:
            image_href = image.picture.source['data-srcset']
            logger.info(image_href)
        except Exception as e:
            logger.error(str(e))
            logger.info('No image')
        price = 1000
        try:
            price = div.find('div', {'class': re.compile(r'^product-buy product-buy_one-line catalog-product__buy.*?$')})\
                .find('div', {'class': re.compile(r'^product-buy__price-wrap product-buy__price-wrap_interactive.*?$')})\
                .find('div', {'class': re.compile(r'^product-buy__price.*?$')})\
                .contents[0]
            comment_amount = 0
        except:
            logger.info('no price')

        product_statistic = {
            'name': name,
            'price': price,
            'image_href': image_href
        }
        parsed_data.append(product_statistic)

    content.close()


with open('statistics.json', 'w', encoding='utf-8') as f:
    dumped_json = json.dumps(parsed_data, indent=4, ensure_ascii=False)
    f.write(dumped_json)
