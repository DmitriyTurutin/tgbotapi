import psycopg2
import os
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
        CREATE TABLE IF NOT EXISTS sales (
            title text,
            price  real,
            amount integer,
            payment_method text,
            client text,
            time_added timestamp NOT NULL PRIMARY KEY 
        )
        """

        self.cur = self.conn.cursor()
        self.cur.execute(create_table_statement)
        self.conn.commit()

    def add(self,
            title: str,
            price: float,
            amount: int,
            payment_method: str,
            client: str,
            time_added: datetime):
        insert_statement = """
        INSERT INTO sales (title, price, amount, payment_method, client, time_added)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (time_added) DO NOTHING"""

        try:
            self.cur.execute(insert_statement, (
                title,
                price,
                amount,
                payment_method,
                client,
                time_added
            ))

            self.conn.commit()

        except psycopg2.Error as e:
            print(e)

    def get_all(self):
        self.cur.execute("SELECT * FROM sales")
        rows = self.cur.fetchall()
        return rows

    def get_time_period(self, from_date: datetime, to_date: datetime):

        select_statement = """SELECT * FROM sales WHERE time_added BETWEEN %s AND %s"""

        self.cur.execute(select_statement, (from_date, to_date))

        rows = self.cur.fetchall()

        return rows

    def get_today(self):
        current_datetime = datetime.now()  # get the current date and time
        current_date = current_datetime.date()  # get the current date without the time
        # subtract one day from the current date
        one_day_ago = current_date - timedelta(days=1)

        select_statement = """SELECT * FROM sales WHERE time_added BETWEEN %s AND %s"""

        # execute the select statement
        self.cur.execute(select_statement, (one_day_ago, current_datetime))

        rows = self.cur.fetchall()  # fetch all the rows returned by the query

        return rows  # return the rows

    def get_last_month(self):
        current_date = datetime.now()
        one_month_ago = current_date - timedelta(days=30)

        select_statement = """SELECT * FROM sales WHERE time_added BETWEEN %s AND %s"""

        self.cur.execute(select_statement, (one_month_ago, current_date))

        rows = self.cur.fetchall()

        return rows

    # def __del__(self):
    #     self.conn.close()
    #     self.cur.close()
