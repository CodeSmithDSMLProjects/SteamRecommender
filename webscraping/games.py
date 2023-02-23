from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

import re
import time
import pandas as pd


service = Service('/users/paulj/chromedriver')
driver = webdriver.Chrome(service=service)
driver.get("https://store.steampowered.com/search/?sort_by=Released_DESC&filter=topsellers&supportedlang=english")

element = driver.find_element(By.ID, 'search_resultsRows')
row_dict = {}
outside_array = []

# scroll to bottom (uncomment block when running, it will take approx 45 min)
# last_height = driver.execute_script("return document.body.scrollHeight")
# while True:
#     # Scroll down to the bottom.
#     driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

#     # Wait to load the page.
#     time.sleep(1.5)

#     # Calculate new scroll height and compare with last scroll height.
#     new_height = driver.execute_script("return document.body.scrollHeight")

#     if new_height == last_height:

#         break

#     last_height = new_height

for row in element.find_elements(By.CSS_SELECTOR, 'a'):
    inside_array = []
    inside_array.append(row.get_attribute('data-ds-appid'))
    inside_array.append(row.get_attribute('href'))
    inside_array.append(row.find_element(By.CLASS_NAME, 'title').get_attribute('innerHTML'))
    inside_array.append(row.get_attribute('data-ds-tagids'))
    # inside_array.append(row.find_element(By.CLASS_NAME, ''))
    if len(row.find_elements(By.CLASS_NAME, 'win')) > 0:
        inside_array.append("windows")
    else:
        inside_array.append("")
    if len(row.find_elements(By.CLASS_NAME, 'mac')) > 0:
        inside_array.append("mac")
    else:
        inside_array.append("")
    if len(row.find_elements(By.CLASS_NAME, 'linux')) > 0:
        inside_array.append("linux")
    else:
        inside_array.append("")
    
    if len(row.find_elements(By.CLASS_NAME, 'positive')) > 0 or len(row.find_elements(By.CLASS_NAME, 'mixed')) > 0 or len(row.find_elements(By.CLASS_NAME, 'negative')) > 0:
        review = row.find_element(By.CLASS_NAME, 'search_review_summary').get_attribute('data-tooltip-html')
        numbers = re.findall(r'\d+', review)
        inside_array.append(review.split('<br>')[0])
        inside_array.append(numbers[0] + '%' + ' of positive reviews')
        inside_array.append(numbers[1] + " total reviews")
    else:
        inside_array.append("Not Rated")
        inside_array.append("Not Rated")
        inside_array.append("Not Rated")

    inside_array.append(row.find_element(By.CLASS_NAME, 'search_released').get_attribute('innerHTML'))
    if len(row.find_element(By.CLASS_NAME, 'search_discount').get_attribute('innerHTML').strip()) > 0: 
        inside_array.append('-' + row.find_element(By.CLASS_NAME, 'search_discount').get_attribute('innerHTML').split('%')[-2][-2:] + '%')
    else:
        inside_array.append("No Discount")
    inside_array.append(row.find_element(By.CLASS_NAME, 'search_price').get_attribute('innerHTML').split('$')[-1].strip())
    outside_array.append(inside_array)

print(outside_array)

# uncomment to create csv file
# pd.DataFrame(outside_array, columns = ['title', 'tags', 'win_comp','mac_comp','linux_comp','review','percent_review',
#                                       'total_review', 'date_released','discount', 'price' ]).to_csv('../data/steam.csv', index=False)