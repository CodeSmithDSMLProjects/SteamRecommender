import pandas as pd
import pickle
import boto3
from botocore.exceptions import ClientError
import pandas as pd
from sqlalchemy import create_engine, URL
import os
import logging

# Read pkl file from S3
def load_file(file_name, bucket):
    """
    Load a file from S3 bucket

    Args:
        file_name (str): File name to load
        bucket (str): Bucket name containing file

    Returns:
        DataFrame: DataFrame of all games and their cosine similarities
    """

    sess = boto3.Session(
        aws_access_key_id = os.environ["ACCESS_KEY"],
        aws_secret_access_key= os.environ["SECRET_KEY"]
    )
    s3client = sess.client('s3')

    try:
        response = s3client.get_object(Bucket=bucket, Key=file_name)
        body = response['Body'].read()
        data = pickle.loads(body)
    except ClientError as e:
        logging.error(e)
        return False
    
    return data


def connectSteam(tblName):
    """
    Returns DataFrame of the specified table name from the PostgreSQL database in AWS

    Args:
        tblName(str): Name of table in PostgreSQL database

    Returns:
        DataFrame: DataFrame of the table called from the PostgresSQL database
    """
    url_object = URL.create(
                    "postgresql+psycopg2",
                    host=os.environ["HOST"],
                    username=os.environ["USER"],
                    port=5432,
                    password=os.environ["PASSWORD"],
                    database=os.environ["DB"])

    engine = create_engine(url_object)

    connection = engine.raw_connection()

    sql = f"""
    SELECT * FROM {tblName}
    """

    return pd.read_sql(sql, con=connection)


def topGames(id, df, max=10):
    """
    Returns the top games that have the highest cosine similarity to the game selected.

    Args:
        id (int): id of game
        df (dataframe): dataframe of cosine similarity
        max (int): The number of games to return. Default = 10

    Returns:
        DataFrame: DataFrame of games with the highest cosine similarity
    """

    # Create ID-Title Dictionary
    # Read from within dockerfile
    # Substitute for sql datatable
    # data = pd.read_csv('steam.csv')
    # data = connectSteam('steam')

    data = connectSteam('steam')
    idNamesDict = data.set_index('Unique_ID').to_dict()['title']

    # Get top matches
    res = df.loc[id].sort_values(ascending=False)[1:max+1]
    res = pd.DataFrame(res)
    res['Title'] = res.index.map(mapper=idNamesDict)
    res.columns = ['Cosine_Similarity', 'Title']
    res = res[['Title', 'Cosine_Similarity']]
    res

    return res
