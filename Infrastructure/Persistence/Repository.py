import psycopg2
from Entities.User import User
import os
from environs import Env
from Entities.Sale import Sale
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

env = Env()


class Repository:
    # connection and cursor 
    conn = None
    cur = None

    host = os.environ['HOST']
    port = env.int('PORT')
    user = os.environ['USER']
    password = os.environ['PASSWORD']
    database = os.environ['DATABASE']



    def __init__(self):
        # set connection
        self.conn = psycopg2.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database
        )
        
        # create users table
        create_users_table_statement= f"""
        CREATE TABLE IF NOT EXISTS users (
            id serial NOT NULL PRIMARY KEY,
            url VARCHAR(256) NOT NULL,
            email VARCHAR(256) NOT NULL,
            password VARCHAR(64) NOT NULL,
            last_updated timestamp,
            model_url VARCHAR(256)
        );
        """
        self.cur = self.conn.cursor()
        self.cur.execute(create_users_table_statement)
        self.conn.commit()

        # create template sales
        create_template_sales_table_statement = f"""
        CREATE TABLE IF NOT EXISTS sales_template (
            title text,
            price  real,
            amount integer,
            payment_method text,
            client text,
            time_added timestamp NOT NULL PRIMARY KEY 
        );"""
        self.cur.execute(create_template_sales_table_statement)
        self.conn.commit()
        

        # create function 
        create_function_statement = f"""
        CREATE OR REPLACE FUNCTION create_sales_table() RETURNS TRIGGER AS $$
        BEGIN
            EXECUTE 'CREATE TABLE sales_' || NEW.id || ' (LIKE sales INCLUDING ALL) INHERITS (sales);';
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
        self.cur.execute(create_template_sales_table_statement)
        self.conn.commit()


        # create trigger
        create_trigger_statement = f"""
        CREATE TRIGGER create_sales_table_trigger
        AFTER INSERT ON users
        FOR EACH ROW
        EXECUTE FUNCTION create_sales_table();
        """
        self.cur.execute(create_trigger_statement)
        self.conn.commit()

        create_index_statement = f"""
        CREATE INDEX users_email_url_idx ON users(email, url);
        """ 
        self.cur.execute(create_index_statement)
        self.conn.commit()



    
    # Check if user exists method
    def check_user(self, email: str, url: str) -> bool:
        self.cur.execute("SELECT COUNT(*) FROM users WHERE email=% and url=%s", (email, url))
        count = self.cur.fetchone()[0]
        return count > 0


    # Get user
    def get_user(self, email: str, url: str):
        self.cur.execute("SELECT * FROM users WHERE email=% and url=%s", (email, url))
        return self.cur.fetchone()


    # Create new user
    def create_user(self, email: str, url: str, password: str) -> None:
        insert_statement = f"""
        INSERT INTO users(url, email, password) 
        VALUES (%s, %s, %s)
        ON CONFLICT(url, email) DO NOTHING;"""

        self.cur.execute(insert_statement, (url, email, password))
