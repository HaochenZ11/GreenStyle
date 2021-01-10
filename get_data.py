import requests
from requests import get
from bs4 import BeautifulSoup as bs, SoupStrainer
import pandas as pd
import numpy as np
import time
from selenium import webdriver as webdriver

DRIVER_PATH = '/Users/katarinac/Desktop/scraping/chromedriver'

wd = webdriver.Chrome(executable_path=DRIVER_PATH)

df = pd.read_csv('/Users/katarinac/Desktop/SheHacks/tops.csv')

brand_link = df['brand link']

def rate_change(t):
    if t == 'We avoid':
        return 1
    elif t == 'Not good enough':
        return 2
    elif t == "It's a start":
        return 3
    elif t == 'Good':
        return 4
    elif t == 'Great':
        return 5

brand_site = []
brand_name = []
brand_rate = []
brand_price = []
brand_rec = [] 
brand_r1 = []
brand_r2 = []
brand_r3 = []
brand_store = []

base = 'https://directory.goodonyou.eco'

for i in range(0, len(brand_link), 15):
    brand_rec = [0, 0, 0] 
    l = df['brand link'][i]
    brand_link = base + l
    store_name = l.split('/')[2]
    #print(brand_link)
    wd.get(brand_link)
    time.sleep(7.5)
    soup = bs(wd.page_source, "lxml")
    span = soup.find_all("span", class_='StyledText-sc-1sadyjn-0 bBUTWf')
    if len(span) < 2:
        time.sleep(15)
        soup = bs(wd.page_source, "lxml")
        span = soup.find_all("span", class_='StyledText-sc-1sadyjn-0 bBUTWf') 
        if len(span) < 2:
            rate_num = 0
            price = 0 
    rating = span[0].text.split(': ')[1]
    rate_num = rate_change(rating)
    price = span[1].text.split(': ')[1]
    brand_rate.append(rate_num)
    brand_price.append(price)
    brand_div2 = soup.find_all('div', class_="StyledBox-sc-13pk1d4-0 hkSFzT")
    for j, element in enumerate(brand_div2):
        if j == 3:
            break
        brand_rec[j] = element.h5.text
    #print(brand_rec)
    brand_r1.append(brand_rec[0])
    brand_r2.append(brand_rec[1])
    brand_r3.append(brand_rec[2])
    brand_store.append(store_name)

df2 = pd.DataFrame({'store name': brand_store, 'rating': brand_rate, 'price': brand_price, 'r1': brand_r1, 'r2': brand_r2, 'r3': brand_r3})
df2.to_csv('/Users/katarinac/Desktop/SheHacks/db.csv')

wd.quit()