from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

import re
import time
import numpy as np
import pandas as pd
import json
import os

from sqlalchemy import URL, create_engine


def update_games():

    # Pull env variables
    url_object = URL.create(
                    "postgresql+psycopg2",
                    host=os.environ["HOST"],
                    username=os.environ["USER"],
                    port=5432,
                    password=os.environ["PASSWORD"],
                    database=os.environ["DB"])

    engine = create_engine(url_object)
    engine.connect()
    connection = engine.raw_connection()

    sql = """
    SELECT * FROM steam
    """

    sql_tag = """
    SELECT * FROM tags
    """

    games_df = pd.read_sql(sql, con=connection)
    tags_df = pd.read_sql(sql_tag, con=connection, index_col='id')
    tag_dict = tags_df.to_dict()

    # Grab data from datatable 
    unique_id_list = games_df['Unique_ID'].to_numpy()

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    service = Service('/usr/local/bin/chromedriver')
    # driver = webdriver.Chrome(service=service)

    # Call in options settings to run chromedriver without window
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get("https://store.steampowered.com/search/?sort_by=Released_DESC&filter=topsellers&supportedlang=english")

    element = driver.find_element(By.ID, 'search_resultsRows')
    # row_dict = {}
    outside_array = []

    # scroll to bottom
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        # Scroll down to the bottom.
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load the page.
        # Changing time to 3s to try and bypass script timeout on EC2
        time.sleep(1.5)

        # Calculate new scroll height and compare with last scroll height.
        new_height = driver.execute_script("return document.body.scrollHeight")

        if new_height == last_height:
            break
        last_height = new_height
    i = 0
    for row in element.find_elements(By.CSS_SELECTOR, 'a'):
        inside_array = []
        print("scrape row" + str(i))
        i = i + 1
        unique_id = np.int64(row.get_attribute('data-ds-appid'))
        totalFinds = row.get_attribute('')
        # conditional to see if new game
        if unique_id not in unique_id_list:
        
        # using this to get brand new data
        # if True:
            inside_array.append(row.get_attribute('data-ds-appid'))
            inside_array.append(row.get_attribute('href'))
            inside_array.append(row.find_element(By.CLASS_NAME, 'title').get_attribute('innerHTML'))

        temp = row.get_attribute('data-ds-tagids')
        if temp is not None:
            new_tags = json.loads(temp)
            list_genre = []
            for tag in new_tags:
                list_genre.append(tag_dict['genre'][int(tag)])
            inside_array.append(list_genre)
        else:
            inside_array.append('None Listed')

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
        inside_array = games_df.loc[games_df['Unique_ID'] == unique_id].values.flatten().tolist()
        
    outside_array.append(inside_array)

    # uncomment to create csv file
    games = pd.DataFrame(outside_array, columns=['Unique_ID', 'url', 'title', 'tags', 'win_comp','mac_comp','linux_comp','review','percent_review',
                                                 'total_review', 'date_released', 'discount', 'price'])

    games.to_sql(name='steam', con=engine, if_exists='replace')

    # return games
    return (games.to_sql(name='steam', con=engine, if_exists='replace', index=False))

update_games()
# df = update_games()
# df.head()
# df.to_csv('../data/test.csv', index=False)
