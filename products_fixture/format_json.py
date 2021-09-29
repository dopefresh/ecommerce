from django.utils.text import slugify

import json

statistics = open('statistics.json', 'r', encoding='utf-8')
statistics_json = json.loads(statistics.read())
statistics.close()

i = 1
for product in statistics_json:
    product['model'] = 'shop.item'
    product['pk'] = i
    product['fields'] = {}
    product['fields']['title'] = product['name']
    product['fields']['slug'] = slugify(product['name'])
    try:
        price = product['price'][:-2:]
        price = price.replace(' ', '')
        product['fields']['price'] = int(price)
    except:
        product['fields']['price'] = 1000
        print('No price or another error')

    if 'процессор' in product.get('name').lower():
        product['fields']['subcategory'] = 1
    elif 'оперативная память' in product.get('name').lower():
        product['fields']['subcategory'] = 2
    elif 'материнская плата' in product.get('name').lower():
        product['fields']['subcategory'] = 3
    elif 'видеокарта' in product.get('name').lower():
        product['fields']['subcategory'] = 4
    i += 1

    product.pop('stars', None)
    product.pop('likes', None)
    product.pop('comments', None)
    product.pop('name', None)
    product.pop('price', None)


with open('products.json', 'w', encoding='utf-8') as f:
    json.dump(statistics_json, f, ensure_ascii=False, indent=4)
