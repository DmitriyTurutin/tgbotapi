import os
import psycopg2
from environs import Env
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

env = Env()

class SalesRepository:
    conn = None
    cur = None

    host = os.environ['HOST']
    port = env.int('PORT') 
    user = os.environ['USER'] 
    password = os.environ['PASSWORD'] 
    database = os.environ['DATABASE'] 

    def __init__(self):
        # Connect to the database and create table if not exists
        self.conn = psycopg2.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database
        )
        create_table_statement = f"""
        CREATE TABLE IF NOT EXISTS accounts (
            id series NOT NULL PRIMARY KEY,
            url VARCHAR(256),
            email VARCHAR(256),
            password VARCHAR(256),
        )
        """

        self.cur = self.conn.cursor()
        self.cur.execute(create_table_statement)
        self.conn.commit()

    def check_existance(self, email: str) -> bool:

        select_statement = """SELECT * FROM sales WHERE eamil=%s"""

        self.cur.execute(select_statement, (email))

        rows = self.cur.fetchall()

        return rows

