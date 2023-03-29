from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

import pandas as pd


service = Service('/users/paulj/chromedriver')
driver = webdriver.Chrome(service=service)
driver.get("https://steamdb.info/tags/")

tag_dict = {}
for element in driver.find_elements(By.CLASS_NAME, 'label'):
    tag_dict[element.find_element(By.CSS_SELECTOR, 'a').get_attribute('href').split('/')[-2]] = element.find_element(By.CSS_SELECTOR, 'a').get_attribute('innerHTML')

print(tag_dict)