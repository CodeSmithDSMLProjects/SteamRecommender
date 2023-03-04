import pandas as pd
import pickle
import boto3
import io
from botocore.exceptions import ClientError
import os


# Read pkl file from S3
def load_file(file_name, bucket):
    """Load a file from S3 bucket

    Args:
        file_name (str): File name to load
        bucket (str): Bucket name containing file

    Returns:
        _type_: _description_
    """

    sess = boto3.Session()
    s3client = sess.client('s3')
    try:
        response = s3client.get_object(Bucket=bucket, Key=file_name)
        body = response['Body'].read()
        data = pickle.loads(body)
    except ClientError as e:
        logging.error(e)
        return False
    
    return data

def topGames(id, df, max=10):
    """

    Returns the top games that have the highest cosine similarity
      to the game selected.

    Args:
        id (int): id of game
        df (dataframe): dataframe of cosine similarity
        max (int): The number of games to return. Default = 10
    """

    # Create ID-Title Dictionary
    data = pd.read_csv('../data/steam.csv')
    idNamesDict = data.set_index('Unique_ID').to_dict()['title']

    # Get top matches
    res = df.loc[id].sort_values(ascending=False)[1:max+1]
    res = pd.DataFrame(res)
    res['Title'] = res.index.map(mapper=idNamesDict)
    res.columns = ['Cosine_Similarity', 'Title']
    res = res[['Title', 'Cosine_Similarity']]
    res

    return res


