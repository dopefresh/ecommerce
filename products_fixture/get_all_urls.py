from bs4 import BeautifulSoup
from selenium import webdriver

import time
import random


url = "https://www.dns-shop.ru"
all_hrefs = []

driver = webdriver.Chrome("/snap/bin/chromium.chromedriver")
driver.get(url)
action = webdriver.ActionChains(driver)
elements = driver.find_elements_by_class_name('menu-desktop__root-info')
for element in elements:
    action.move_to_element(element)
    action.perform()

    content = driver.page_source

    soup = BeautifulSoup(content, features="html.parser")
    for div in soup.findAll('div', {'class': 'menu-desktop__second-level-wrap'}):
        hrefs = div.findAll('a', {'class': 'ui-link menu-desktop__second-level'})
        for a in hrefs:
            if a is None:
                continue
            all_hrefs.append('https://www.dns-shop.ru' + a.get('href'))

    time.sleep(random.randint(1, 4))


with open('all_hrefs.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(all_hrefs))


