import json
import pandas as pd
from sqlalchemy import create_engine
from flask import Flask, request, jsonify
import pandas as pd
import boto3
import pickle as pkl
import os
from functions import load_file, topGames

df = pd.read_csv('../data/steam.csv')
idDict = df.set_index('title').to_dict()['Unique_ID']
unpickled = pd.read_pickle("../data/cos_df.pkl")

# session = boto3.Session(
#     aws_access_key_id = os.environ["ACCESS_KEY"],
#     aws_secret_access_key=os.environ["ACCESS_SECRET"],
#     region_name = os.environ["REGION"]
# )

# url_object = URL.create(
#                 "postgresql+psycopg2",
#                 host=os.environ["HOST"],
#                 username=os.environ["USER"],
#                 port=5432,
#                 password=os.environ["PASSWORD"],
#                 database=os.environ["DB"])

# engine = create_engine(url_object)
# engine.connect()
# connection = engine.raw_connection()

# s3 = session.resource('s3')
# URI = os.environ["URI"]
# engine = create_engine(URI)

# similarity_df = pd.read_sql_table('models_score', con=engine)

# mod_api = pkl.loads(s3.Bucket("carsalesmodel").Object(f'{name}.pkl').get()['Body'].read())

app = Flask(__name__)

@app.route('/', methods = ['GET'])
def view():
    return 'Hello World!'


@app.route('/predict', methods = ['POST'])
def predict():

    data = request.json
    pred = topGames(idDict[data[1:-1]], unpickled, 10)
    res = pred.to_json()
    load = json.loads(res)
    return json.dumps(load)
    # return json.dumps(pred)

if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 8080)