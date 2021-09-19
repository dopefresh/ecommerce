from django.utils.text import slugify

import json
from shop.models import SubCategory

statistics = open('statistics.json', 'r', encoding='utf-8')
statistics_json = json.loads(statistics.read())
statistics.close()


for product in statistics_json:
    product.pop(stars, None)
    product.pop(likes, None)
    product.pop(comments, None)
    if 'Оперативная память' in product.get('name'):
        product['sub_category'] = None
