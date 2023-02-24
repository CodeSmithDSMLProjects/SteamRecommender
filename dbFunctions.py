import pandas as pd
from sqlalchemy import create_engine, URL


def connectSteam(tblName, username, password):
    url_object = URL.create(
                    "postgresql+psycopg2",
                    host='steam-db.c5m99euxia00.us-east-1.rds.amazonaws.com',
                    username=username,
                    port=5432,
                    password=password,
                    database='steam_db')

    engine = create_engine(url_object)

    connection = engine.raw_connection()

    sql = f"""
    SELECT * FROM {tblName}
    """

    return pd.read_sql(sql, con=connection)
