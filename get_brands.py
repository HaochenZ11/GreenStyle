import requests
from requests import get
from bs4 import BeautifulSoup as bs
import pandas as pd
import numpy as np
import time
from selenium import webdriver as webdriver

DRIVER_PATH = '/Users/katarinac/Desktop/scraping/chromedriver'

# code to scroll to bottom on a site
def scroll(driver, timeout):
    scroll_pause_time = timeout;
    last_height = driver.execute_script("return document.body.scrollHeight")
    print('scrolling!')

    while True:
        #print(last_height)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(30)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


wd = webdriver.Chrome(executable_path=DRIVER_PATH)
wd.get('https://directory.goodonyou.eco/categories/tops')
scroll(wd, 2)


soup = bs(wd.page_source, "html.parser")
#print(soup.prettify())


name = []
link = []
store_div = soup.find_all('div', class_= 'sc-TOsTZ drPOgn')
#print(store_div)

for container in store_div:
    name.append(container.h5.text)
    link_name = container.find('a', href = True)
    link.append(link_name['href'])

print(len(link))
print(len(name))
print(name[-1])


df = pd.DataFrame({'store name': name, 'brand link': link})
df.to_csv('/Users/katarinac/Desktop/SheHacks/tops.csv')


time.sleep(60)

wd.quit()