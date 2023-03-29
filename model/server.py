import json
import pandas as pd
import psycopg2
from sqlalchemy import create_engine, URL
from flask import Flask, request, jsonify
import boto3
import pickle as pkl
import os
from functions import topGames

# df = pd.read_csv('../data/steam.csv')
# idDict = df.set_index('title').to_dict()['Unique_ID']
# unpickled = pd.read_pickle("../data/cos_df.pkl")

# S3 - Pickl
session = boto3.Session(
    aws_access_key_id = os.environ["ACCESS_KEY"],
    aws_secret_access_key=os.environ["SECRET_KEY"],
    # region_name = os.environ["REGION"]
)

s3client = session.client('s3')

bucket = 'steam-models'
file_name = 'cos_df.pkl'

response = s3client.get_object(Bucket=bucket, Key=file_name)
body = response['Body'].read()
unpickled = pkl.loads(body)

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
idDict = df.set_index('title').to_dict()['Unique_ID']

app = Flask(__name__)

@app.route('/')
def index():
    return 'Web App with Python Flask!'

@app.route('/predict_streamlit', methods = ['POST'])
def predict_streamlit():

    data = request.json
    # print(str(type(idDict[data[1:-1]])))
    # return str(type(idDict[data[1:-1]]))

    pred = topGames(idDict[data[1:-1]], unpickled, 10)
    res = pred.to_json()
    load = json.loads(res)
    return json.dumps(load)
    # return json.dumps(pred)

@app.route('/get_titles', methods = ['GET'])
def get_games():

    data = df['title']

    res = data.to_json(orient= 'values')
    load = json.loads(res)
    return json.dumps(load)

@app.route('/predict', methods = ['POST'])
def predict():


    data = request.get_data()
    data = data.decode("utf-8")
    pred = topGames(idDict[data], unpickled, 10)
    res = pred.to_json()
    load = json.loads(res)
    return json.dumps(load)

if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 8080)