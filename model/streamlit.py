import streamlit as st
import boto3
import pickle
import pandas as pd
from streamlit_option_menu import option_menu
import os
from sqlalchemy import create_engine, text, URL
import json
import requests as rq

st.set_page_config(layout="wide", page_title="Steam Games Recommender")

df = pd.read_csv('../data/steam.csv')


# url_object = URL.create(
#                 "postgresql+psycopg2",
#                 host=os.environ["HOST"],
#                 username=os.environ["USER"],
#                 port=5432,
#                 password=os.environ["PASSWORD"],
#                 database=os.environ["DB"])

# session = boto3.Session(
#     aws_access_key_id = os.environ["ACCESS_KEY"],
#     aws_secret_access_key=os.environ["ACCESS_SECRET"],
#     region_name = os.environ["REGION"]
# )

# engine = create_engine(url_object)

# GAMES_SQL_QUERY = 'SELECT DISTINCT "title" FROM steam'

# with engine.connect() as connection:
#     games_df = pd.read_sql_query(GAMES_SQL_QUERY, con=connection)

selected_navbar = option_menu(None, ["Predict", "FAQ", "API"], orientation="horizontal")

if selected_navbar == "Predict":
    with st.container():
        st.text('TEXT FOR PICKING GAMES')
        form = st.form(key='uinput')
    with form:

        option = st.selectbox(
            'Pick a game that you enjoyed playing',
            df['title'])

        st.write('You selected:', option)
        button = st.form_submit_button(label="Submit", use_container_width=True)

    if button:
        # Connect to Flask Predict
        url     =  'http://127.0.0.1:8080/predict'
        payload = json.dumps(option)
        resp    = rq.post(url, json = payload)
        try:    
            st.write(pd.DataFrame(resp.json()))
        except Exception as e:
            st.text(f"Could not process request because: {e}")