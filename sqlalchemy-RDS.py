#!/usr/bin/env python
# coding: utf-8

from keys import secrets
import pandas as pd
from sqlalchemy import URL, create_engine

# Create postgres url_object for engine
url_object = URL.create(
                "postgresql+psycopg2",
                host='steam-db.c5m99euxia00.us-east-1.rds.amazonaws.com',
                username=secrets.get('user'),
                port=5432,
                password=secrets.get('password'),
                database='steam_db')


engine = create_engine(url_object)
engine.connect()

steam_path = 'data/steam.csv'
tags_path = 'data/tags.csv'

# Read in csv files
steam = pd.read_csv(steam_path)
tags = pd.read_csv(tags_path)

# Drop existing table if needed
connection = engine.raw_connection()
cursor = connection.cursor()
command = "DROP TABLE IF EXISTS {};".format('steam')
cursor.execute(command)
connection.commit()
cursor.close()

# Convert steam df to sql db
steam.to_sql(name='steam', con=engine, if_exists='replace')

# Convert tags df to sql db
tags.to_sql(name='tags', con=engine, if_exists='replace')

# Read from table steam
sql = """
SELECT * FROM steam
"""

pd.read_sql(sql, con=connection)

# Read from table tags
sql = """
SELECT * FROM tags
"""

pd.read_sql(sql, con=connection)
