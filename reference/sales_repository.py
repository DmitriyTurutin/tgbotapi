import datetime

class SalesRepository:
    def __init__(self, connection_str: str, user_repo: UserRepository):
        self.connection_str = connection_str
        self.user_repo = user_repo

    def add_sale(self, user_id: int, sale: dict):
        if not self.user_repo.get_user(user_id):
            user_id = self.user_repo.add_user({'email': sale['email'], 'password': sale['password'], 'url': sale['url']})
        with psycopg2.connect(self.connection_str) as conn:
            with conn.cursor() as cur:
                cur.execute(f"INSERT INTO user_sales_{user_id} (title, price, amount, payment_method, time_added) VALUES (%s, %s, %s, %s, %s)",
                            (sale['title'], sale['price'], sale['amount'], sale['payment_method'], sale['time_added']))
                conn.commit()

    def get_sales(self, user_id: int):
        if not self.user_repo.get_user(user_id):
            raise ValueError(f"User with id {user_id} does not exist.")
        with psycopg2.connect(self.connection_str) as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute(f"SELECT * FROM user_sales_{user_id}")
                sales = cur.fetchall()
                return sales

    def get_sales_for_month(self, user_id: int, month: int, year: int):
        if not self.user_repo.get_user(user_id):
            raise ValueError(f"User with id {user_id} does not exist.")
        with psycopg2.connect(self.connection_str) as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute(f"SELECT * FROM user_sales_{user_id} WHERE EXTRACT(MONTH FROM time_added) = %s AND EXTRACT(YEAR FROM time_added) = %s", (month, year))
                sales = cur.fetchall()
                return sales

