# grab webscraped data, clean the data into sparse dataframe, run cosine similarity, 
# then push cosine similarity to rds

import pandas as pd
import datetime as dt
from functions_preprocess import select_n_components, upload_file
from sqlalchemy import URL, create_engine
import os
import pickle

from scipy.spatial.distance import cdist, pdist
from sklearn.metrics.pairwise import pairwise_distances, cosine_similarity
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import MultiLabelBinarizer

from sqlalchemy import URL, create_engine


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

# Preprocess Data
mlb = MultiLabelBinarizer(sparse_output=True)
df = df.join(
            pd.DataFrame.sparse.from_spmatrix(
                mlb.fit_transform(df['tags']),
                index=df.index,
                columns=mlb.classes_))
df = df.drop(['title','url','tags'], axis=1).set_index('Unique_ID')
df = df.drop('review', axis=1)
df['price'] = pd.to_numeric(df['price'], downcast='float', errors='coerce')
df['price'].fillna(0, inplace=True)
df['date_released'] = pd.to_datetime(df['date_released'])
df['year'] = df['date_released'].dt.year
df['year'].fillna(0, inplace=True)
df['discount'] = df['discount'].apply(lambda x: x.replace('-', "").replace("No Discount", "0").strip('%'))
df['total_review'] = df['total_review'].apply(lambda x: x.split(' ')[0].replace('Not', '0'))
df['percent_review'] = df['percent_review'].apply(lambda x: x.split(' ')[0].replace('Not', '0').strip('%'))
df = df.drop('date_released', axis=1)
df = df[~df.index.duplicated(keep='first')]

# Save ID labels to name matrix transformation
idLabels = list(df.index)

scaled_data = StandardScaler().fit_transform(df)

# Find Ideal TSVD n_components
tsvd = TruncatedSVD(n_components=df.shape[1]-1)
data_tsvd = tsvd.fit(scaled_data)
tsvd_var_ratios = tsvd.explained_variance_ratio_
# Find n_components needed for desired variance
select_n_components = select_n_components(tsvd_var_ratios, 0.95)
# Fit TSVD using n_components found
tsvd = TruncatedSVD(n_components=select_n_components)
data_tsvd = tsvd.fit_transform(scaled_data)
# Find cosine similarity of scaled TSVD data
cos_TSVD_df = pd.DataFrame(cosine_similarity(data_tsvd), columns=idLabels)
cos_TSVD_df.index = idLabels

# Look to port this to RDS
# print(cos_TSVD_df)

# serialized_model = pickle.dumps(cos_TSVD_df)

# Pack file as pickle
# cos_TSVD_df.to_pickle("../data/cos_df.pkl")

# unpickled = pd.read_pickle("../data/cos_df.pkl")
# # print(unpickled)

# # Load into S3
bucket = 'steam-models'
file = 'cos_df.pkl'
upload_file(cos_TSVD_df, bucket=bucket, object_name = file)
