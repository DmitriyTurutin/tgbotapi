import psycopg2
import psycopg2.extras

class UserRepository:
    def __init__(self, connection_str: str):
        self.connection_str = connection_str

    def get_user(self, user_id: int):
        with psycopg2.connect(self.connection_str) as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
                user = cur.fetchone()
                return user

    def add_user(self, user: dict):
        with psycopg2.connect(self.connection_str) as conn:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO users (url, email, password) VALUES (%s, %s, %s) RETURNING id",
                            (user['url'], user['email'], user['password']))
                new_user_id = cur.fetchone()[0]
                cur.execute(f"CREATE TABLE user_sales_{new_user_id} (user_id INTEGER) INHERITS (sales_template);")
                conn.commit()
                return new_user_id

    def update_user(self, user_id: int, data: dict):
        with psycopg2.connect(self.connection_str) as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE users SET url = %s, email = %s, password = %s, updated = NOW() WHERE id = %s",
                            (data['url'], data['email'], data['password'], user_id))
                conn.commit()

