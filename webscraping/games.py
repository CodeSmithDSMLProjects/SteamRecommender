from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

import re
import time
import numpy as np
import pandas as pd

from sqlalchemy import URL, create_engine

def update_games():

    url_object = URL.create(
                    "postgresql+psycopg2",
                    host='steam-db.c5m99euxia00.us-east-1.rds.amazonaws.com',
                    username='myuser',
                    port=5432,
                    password='secret_passwd',
                    database='steam_db')

    engine = create_engine(url_object)
    engine.connect()
    connection = engine.raw_connection()

    sql = """
    SELECT * FROM steam
    """

    games_df = pd.read_sql(sql, con=connection)



    # Grab data from datatable / csv
    # games_df = pd.read_csv('../data/steam.csv')
    unique_id_list = games_df['Unique_ID'].to_numpy()


    service = Service('/users/paulj/chromedriver')
    driver = webdriver.Chrome(service=service)
    driver.get("https://store.steampowered.com/search/?sort_by=Released_DESC&filter=topsellers&supportedlang=english")

    element = driver.find_element(By.ID, 'search_resultsRows')
    outside_array = []

    # scroll to bottom
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        # Scroll down to the bottom.
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load the page.
        time.sleep(1.5)

        # Calculate new scroll height and compare with last scroll height.
        new_height = driver.execute_script("return document.body.scrollHeight")

        if new_height == last_height:

            break

        last_height = new_height

    for row in element.find_elements(By.CSS_SELECTOR, 'a'):
        inside_array = []

        unique_id = np.int64(row.get_attribute('data-ds-appid'))


        # conditional to see if new game
        if unique_id not in unique_id_list:

            inside_array.append(row.get_attribute('data-ds-appid'))
            inside_array.append(row.get_attribute('href'))
            inside_array.append(row.find_element(By.CLASS_NAME, 'title').get_attribute('innerHTML'))
            inside_array.append(row.get_attribute('data-ds-tagids'))
            # inside_array.append(row.find_element(By.CLASS_NAME, ''))
            if len(row.find_elements(By.CLASS_NAME, 'win')) > 0:
                inside_array.append(1)
            else:
                inside_array.append(0)
            if len(row.find_elements(By.CLASS_NAME, 'mac')) > 0:
                inside_array.append(1)
            else:
                inside_array.append(0)
            if len(row.find_elements(By.CLASS_NAME, 'linux')) > 0:
                inside_array.append(1)
            else:
                inside_array.append(0)
            
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
            
        else:

            inside_array = games_df.loc[games_df['Unique_ID'] == 1643320].values.flatten().tolist()
        
        outside_array.append(inside_array)


    # print(outside_array)

    # uncomment to create csv file
    return(pd.DataFrame(outside_array, columns = ['Unique_ID','url','title', 'tags', 'win_comp','mac_comp','linux_comp','review','percent_review',
                                        'total_review', 'date_released','discount', 'price' ]))