import os
import psycopg2
from environs import Env
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

env = Env()

class UsersRepository:
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