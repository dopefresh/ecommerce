from selenium import webdriver
import time
import random

driver = webdriver.Chrome("/snap/bin/chromium.chromedriver")
#  url = "https://www.dns-shop.ru/catalog/17a89a0416404e77/materinskie-platy/"
#  url = "https://www.dns-shop.ru/catalog/17a89aab16404e77/videokarty/"
#  url = "https://www.dns-shop.ru/catalog/17a9b91b16404e77/operativnaya-pamyat-so-dimm/"
url = "https://www.dns-shop.ru/catalog/17a89a3916404e77/operativnaya-pamyat-dimm/"

for page in range(1, 11):
    if page == 1:
        driver.get(url)
    else:
        driver.get(url + f'?p={page}')
    
    content = driver.page_source
    with open(f'documents/ramdimm_page{page}.html', 'w') as f:
        f.write(content)

    time.sleep(random.randint(3, 9))



