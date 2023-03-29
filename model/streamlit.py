import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
from sqlalchemy import create_engine, text, URL
import json
import requests as rq
import os

st.set_page_config(layout="wide", page_title="Steam Games Recommender")

# df = pd.read_csv('../data/steam.csv')


# SQL - RDS
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

df = pd.read_sql(sql, con=connection)

selected_navbar = option_menu(None, ["Predict", "FAQ", "API"], orientation="horizontal")

url = os.environ["SERVER_URL"]
# url     =  'http://server_docker:8080/predict_streamlit'


if selected_navbar == "Predict":
    with st.container():
        st.text('Steam has a wide range of games for everyone. With this, we have developed a game recommender model to help you decide which game to play next.\nSearching through the top sellers on Steam one can get lost with the sheer amount of games (i.e. OVER 9000).\nWith this recommender all you need to do is input a game that you have enjoyed recently and we will provide you with 10 games that are similar that you might enjoy!')
        form = st.form(key='uinput')
    with form:

        option = st.selectbox(
            'Pick a game that you enjoyed playing',
            df['title'])

        st.write('You selected:', option)
        button = st.form_submit_button(label="Submit", use_container_width=True)

    if button:
        # Test connection to server
        # Connect to Flask Predict
        payload = json.dumps(option)
        resp    = rq.post(url, json = payload)
        try:    
            st.write(pd.DataFrame(resp.json()))
        except Exception as e:
            st.text(f"Could not process request because: {e}")

if selected_navbar == "API":
    st.subheader("Our API is free to use and available via a POST request to (fill in later with url)")
    st.write('The post request must include the title of the game')

    st.subheader('Ex:')
    st.text('''curl -d "S.T.A.L.K.E.R. 2: Heart of Chornobyl" -X POST url/predict''')
       
if selected_navbar == "FAQ":
    with st.container():
        with st.expander("What is Steam?"):
            st.write('Steam is a digital platfor created by Valve Corportation to serve as a distributor of PC games')
        with st.expander("What model is being used to predict similarity in games?"):
            st.write('We are using a SVD truncated cosine similarity to find the most similar games')
        with st.expander("How was the data collected?"):
            st.write('All of the data has been gathered through web scraping steams database of top selling games')
        with st.expander("Can I use this site commercially?"):
            st.write('This site is not intended to be used commercially and should not be used commercially')


st.write("Developed by Kevin Lam and Paul Yim [Github Repo]('https://github.com/CodeSmithDSMLProjects/SteamRecommender')")
st.write("Contact us at ")