import psycopg2
from Entities.User import User
import os
from environs import Env
from Entities.Sale import Sale
import concurrent.futures
import io
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
        create_users_table_statement = f"""
        CREATE TABLE IF NOT EXISTS users (
            id serial NOT NULL PRIMARY KEY,
            url VARCHAR(256) NOT NULL,
            email VARCHAR(256) NOT NULL,
            password VARCHAR(64) NOT NULL,
            last_updated timestamp,
            model_url VARCHAR(256),
            UNIQUE (email, url)
        );
        """
        self.cur = self.conn.cursor()
        self.cur.execute(create_users_table_statement)
        self.conn.commit()

        # create template sales
        create_template_sales_table_statement = f"""
        CREATE TABLE IF NOT EXISTS sales_template (
            id serial PRIMARY KEY,
            title text,
            price  real,
            amount integer,
            payment_method text,
            client text,
            time_added timestamp
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
        check_trigger_query = "SELECT tgname FROM pg_trigger WHERE tgname = 'create_sales_table_trigger'"
        self.cur.execute(check_trigger_query)
        trigger_exists = self.cur.fetchone()
        if not trigger_exists:
            create_trigger_statement = """
            CREATE TRIGGER create_sales_table_trigger
            AFTER INSERT ON users
            FOR EACH ROW
            EXECUTE FUNCTION create_sales_table();
            """
            self.cur.execute(create_trigger_statement)
            self.conn.commit()

        # create_index_statement = f"""
        # CREATE INDEX users_email_url_idx ON users(email, url);
        # """
        # self.cur.execute(create_index_statement)
        # self.conn.commit()

    # Check if user exists method

    def check_user(self, email: str, url: str) -> bool:
        self.cur.execute(
            "SELECT COUNT(*) FROM users WHERE email=%s and url=%s", (email, url))
        count = self.cur.fetchone()[0]
        return count > 0

    # Get user

    def get_user(self, email: str, url: str):
        self.cur.execute(
            "SELECT * FROM users WHERE email=%s and url=%s", (email, url))
        return self.cur.fetchone()

    # Create new user

    def create_user(self, email: str, url: str, password: str) -> None:
        insert_statement = f"""
        INSERT INTO users(url, email, password) 
        VALUES (%s, %s, %s);"""

        self.cur.execute(insert_statement, (url, email, password))
        self.conn.commit()

    # Add data to the table

    def add_sales_data(self, email: str, url: str, sales: list[Sale]):
        self.conn.commit()
        self.cur.execute(
            "SELECT * FROM users WHERE email=%s and url=%s", (email, url))
        id = self.cur.fetchone()[0]
        table = "sales_" + str(id)

        self.cur.execute(f"CREATE INDEX IF NOT EXISTS time_added_index ON {table} (time_added);")


        with concurrent.futures.ThreadPoolExecutor() as executor:
            for sales_batch in self.chunks(sales, 1000):
                executor.submit(self.insert_sales, table,
                                sales_batch, self.cur)

        updated_at = datetime.now()
        self.cur.execute(
            "UPDATE users SET last_updated = %s WHERE id = %s", (updated_at, id))
        self.conn.commit()

    def chunks(self, lst, n):
        """Yield successive n-sized chunks from lst."""
        for i in range(0, len(lst), n):
            yield lst[i:i + n]

    def insert_sales(self, table: str, sales: list[Sale], cur: psycopg2.extensions.cursor) -> None:
        cur.executemany(f"INSERT INTO {table}(title, price, amount, payment_method, client, time_added) VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (time_added) DO NOTHING", [
                        (sale.title, sale.price, sale.amount, sale.payment_method, sale.client, sale.time_added) for sale in sales])
        cur.connection.commit()

    # Retrive data for one month

    def get_last_month(self, email: str, url: str):
        current_date = datetime.now().date()
        one_month_ago = current_date - timedelta(days=30)
        self.cur.execute(
            "SELECT * FROM users WHERE email=%s and url=%s", (email, url))
        id = self.cur.fetchone()[0]
        table = 'sales_' + str(id)

        self.cur.execute(f"SELECT * FROM {table} WHERE time_added BETWEEN %s AND %s",
                         (one_month_ago, current_date))
        return self.cur.fetchall()

    # Retrive for today

    def get_today(self, email: str, url: str):
        current_date = datetime.now().date() + timedelta(days=1)
        one_day_ago = datetime.now().date()
        self.cur.execute(
            "SELECT * FROM users WHERE email=%s and url=%s", (email, url))
        id = self.cur.fetchone()[0]
        table = "sales_" + str(id)

        self.cur.execute(
            f"SELECT * FROM {table} WHERE time_added BETWEEN %s AND %s", (one_day_ago, current_date))
        return self.cur.fetchall()

    # Get all data

    def get_all(self, email: str, url: str):
        self.cur.execute(
            "SELECT * FROM users WHERE email=%s and url=%s", (email, url))
        id = self.cur.fetchone()[0]
        table = "sales_" + str(id)

        self.cur.execute(f"SELECT * FROM {table}")
        return self.cur.fetchall()
    # Retrive for range

    def get_time_period(self, from_date: datetime, to_date: datetime, email: str, url: str):
        self.cur.execute(
            "SELECT * FROM users WHERE email=%s and url=%s", (email, url))
        id = self.cur.fetchone()[0]
        table = "sales_" + str(id)

        select_statement = f"""SELECT * FROM {table} WHERE time_added BETWEEN %s AND %s"""

        self.cur.execute(select_statement, (from_date, to_date))

        rows = self.cur.fetchall()

        return rows

    # Bulk data

    def bulk_data(self, email: str, url: str, sales: list[Sale]):
        self.cur.execute(
            "SELECT * FROM users WHERE email=%s and url=%s", (email, url))
        id = self.cur.fetchone()[0]
        table = "sales_" + str(id)

        cur = self.conn.cursor()
        f = io.StringIO()
        for sale in sales:
            if not sale.title:
                pass
            else:
                f.write(sale.title + '\t' + str(sale.price) + '\t' + str(sale.amount) + '\t' + sale.payment_method +
                        '\t' + sale.client + '\t' + sale.time_added.strftime("%Y-%m-%d %H:%M:%S"))
                f.write('\n')
        f.seek(0)
        cur.copy_from(f, table, columns=('title', 'price',
                      'amount', 'payment_method', 'client', 'time_added'))
        self.conn.commit()

    def __del__(self):
        self.conn.close()
        self.cur.close()
