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

        statistics = div.find('div', attrs={'class': 'catalog-product__stat'})
        rating_div = statistics.find(
            'a', attrs={'class': 'catalog-product__rating ui-link ui-link_black'})
        rating = rating_div.get('data-rating')
        likes = rating_div.contents[-1]

        comment = statistics.find(
            'a', attrs={'class': 'catalog-product__comment ui-link ui-link_black'})

        price = ''
        try:
            price = div.find('div', {'class': re.compile(r'^product-buy product-buy_one-line catalog-product__buy.*?$')})\
                .find('div', {'class': re.compile(r'^product-buy__price-wrap product-buy__price-wrap_interactive.*?$')})\
                .find('div', {'class': re.compile(r'^product-buy__price.*?$')})\
                .contents[0]
            comment_amount = 0
        except:
            logger.info('no price')

        try:
            comment_amount = find_max_number(comment.contents[1])
        except Exception as e:
            comment_amount = 0
            logger.info(str(e))

        product_statistic = {
            'name': name,
            'price': price,
            'stars': rating,
            'likes': likes,
            'comments': comment_amount
        }
        parsed_data.append(product_statistic)

    content.close()


with open('statistics.json', 'w', encoding='utf-8') as f:
    dumped_json = json.dumps(parsed_data, indent=4, ensure_ascii=False)
    f.write(dumped_json)
