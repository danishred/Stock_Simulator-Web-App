import os # For accessing environment variable
import psycopg2 # Driver to interact with PSQL
import psycopg2.extras # Allows referencing as dictionary
from dotenv import load_dotenv # Allows loading environment variables 

load_dotenv()

class user_model():

    # Creating tables 
    def create_table(self):
    
        url = os.getenv("POSTGRES_URL")
        connection = psycopg2.connect(url)
        with connection:
            with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor: 
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS sim_users( id SERIAL PRIMARY KEY, username TEXT NOT NULL UNIQUE, 
                hash TEXT NOT NULL, cash NUMERIC NOT NULL DEFAULT 10000.00)""")
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS history( id INTEGER NOT NULL, symbol TEXT NOT NULL, shares NUMERIC NOT NULL,
                price NUMERIC NOT NULL, date TEXT NOT NULL, FOREIGN KEY (id) REFERENCES sim_users(id))""") 
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS liveindex (id INTEGER NOT NULL,symbol TEXT NOT NULL, liveshares NUMERIC NOT NULL,
                liveprice NUMERIC, FOREIGN KEY (id) REFERENCES sim_users(id)
                )
                """)
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS notes ( serial SERIAL PRIMARY KEY, id INTEGER NOT NULL, data BYTEA,
                date TIMESTAMP NOT NULL
                )
                """)
                cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_history_id ON history (id)
                """)
                cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_history_symbol ON history (symbol)
                """)
                cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_liveindex_id ON liveindex (id)
                """)
                cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_liveindex_symbol ON liveindex (symbol)
                """)

    def fetch_total_cash(self, user_id): 
        url = os.getenv("POSTGRES_URL")
        connection = psycopg2.connect(url)
        with connection:
            with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute("SELECT cash FROM sim_users WHERE id = %s", (user_id,))
                cash = cursor.fetchone()[0]
                return cash;                

    def fetch_user_cash(self, user_id):
            url = os.getenv("POSTGRES_URL")
            connection = psycopg2.connect(url)
            with connection:
                with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                    cursor.execute("SELECT cash FROM sim_users WHERE id = %s", (user_id,))
                    cash = cursor.fetchone()["cash"]
                    return cash

    def fetch_user_name(self, user_id):
        url = os.getenv("POSTGRES_URL")
        connection = psycopg2.connect(url)
        with connection:
            with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute("SELECT username FROM sim_users WHERE id = %s", (user_id,))
                username = cursor.fetchone()["username"]
                return username

    def fetch_liveindex(self, user_id):
        url = os.getenv("POSTGRES_URL")
        connection = psycopg2.connect(url)
        with connection:
            with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute("SELECT * FROM liveindex WHERE id = %s", (user_id,))
                liveindexes = cursor.fetchall()
                return liveindexes

    def update_liveindex(self, liveprice, user_id, symbol):
        url = os.getenv("POSTGRES_URL")
        connection = psycopg2.connect(url)
        with connection:
            with connection.cursor() as cursor:
                cursor.execute("UPDATE liveindex SET liveprice = %s WHERE id = %s AND symbol = %s",
                            (liveprice, user_id, symbol))

    def update_user_cash(self, new_cash, user_id):
        url = os.getenv("POSTGRES_URL")
        connection = psycopg2.connect(url)
        with connection:
            with connection.cursor() as cursor:
                cursor.execute("UPDATE sim_users SET cash = %s WHERE id = %s", (new_cash, user_id))

    def insert_liveindex(self, user_id, symbol, shares, price):
        url = os.getenv("POSTGRES_URL")
        connection = psycopg2.connect(url)
        with connection:
            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO liveindex(id, symbol, liveshares, liveprice) VALUES(%s, %s, %s, %s)",
                            (user_id, symbol, shares, price))

    def update_liveindex_shares(self, liveshares, user_id, symbol):
        url = os.getenv("POSTGRES_URL")
        connection = psycopg2.connect(url)
        with connection:
            with connection.cursor() as cursor:
                cursor.execute("UPDATE liveindex SET liveshares = %s WHERE id = %s AND symbol = %s",
                            (liveshares, user_id, symbol))

    def insert_history(self, user_id, symbol, shares, price):
        url = os.getenv("POSTGRES_URL")
        connection = psycopg2.connect(url)
        with connection:
            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO history(id, symbol, shares, price, date) VALUES(%s, %s, %s, %s, (SELECT NOW()))",
                            (user_id, symbol, shares, price))

    def fetch_history(self, user_id):
        url = os.getenv("POSTGRES_URL")
        connection = psycopg2.connect(url)
        with connection:
            with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute("SELECT * FROM history WHERE id = %s", (user_id,))
                histories = cursor.fetchall()
                return histories

    def fetch_user_by_username(self, username):
        url = os.getenv("POSTGRES_URL")
        connection = psycopg2.connect(url)
        with connection:
            with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute("SELECT * FROM sim_users WHERE username = %s", (username,))
                user = cursor.fetchall()
                return user

    def insert_user(self, username, hashed_password):
        url = os.getenv("POSTGRES_URL")
        connection = psycopg2.connect(url)
        with connection:
            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO sim_users(username, hash) VALUES(%s, %s)", (username, hashed_password))

    def fetch_user_shares(self, user_id, symbol):
        url = os.getenv("POSTGRES_URL")
        connection = psycopg2.connect(url)
        with connection:
            with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute("SELECT liveshares FROM liveindex WHERE id = %s AND symbol = %s", (user_id, symbol))
                shares = cursor.fetchone()
                return shares

    def delete_zero_shares(self):
        url = os.getenv("POSTGRES_URL")
        connection = psycopg2.connect(url)
        with connection:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM liveindex WHERE liveshares = 0")

    def insert_note(self, user_id, notes):
        url = os.getenv("POSTGRES_URL")
        connection = psycopg2.connect(url)
        with connection:
            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO notes(id, data, date) VALUES(%s, %s, (SELECT NOW()))", (user_id, notes))

    def fetch_notes(self, user_id):
        url = os.getenv("POSTGRES_URL")
        connection = psycopg2.connect(url)
        with connection:
            with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute("SELECT * FROM notes WHERE id = %s ORDER BY serial DESC", (user_id,))
                notes = cursor.fetchall()
                return notes

    def delete_note_by_serial(self, serial):
        url = os.getenv("POSTGRES_URL")
        connection = psycopg2.connect(url)
        with connection:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM notes WHERE serial = %s", (serial,))

    def reset_user_data(self, user_id):
        url = os.getenv("POSTGRES_URL")
        connection = psycopg2.connect(url)
        with connection:
            with connection.cursor() as cursor:
                cursor.execute("UPDATE sim_users SET cash = 10000 WHERE id = %s", (user_id,))
                cursor.execute("DELETE FROM history WHERE id = %s", (user_id,))
                cursor.execute("DELETE FROM liveindex WHERE id = %s", (user_id,))
                cursor.execute("DELETE FROM notes WHERE id = %s", (user_id,))

    def update_user_password(self, user_id, hashed_password):
        url = os.getenv("POSTGRES_URL")
        connection = psycopg2.connect(url)
        with connection:
            with connection.cursor() as cursor:
                cursor.execute("UPDATE sim_users SET hash = %s WHERE id = %s", (hashed_password, user_id))
   
    def fetch_user_symbols(self, user_id):
        url = os.getenv("POSTGRES_URL")
        connection = psycopg2.connect(url)
        with connection:
            with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute("SELECT * FROM liveindex WHERE id = %s", (user_id,))
                symbols = cursor.fetchall()
                return symbols
            
    def fetching_shares_bought(self, user_id, symbol):
        url = os.getenv("POSTGRES_URL")
        connection = psycopg2.connect(url)
        with connection:
            with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute("SELECT SUM(liveshares) FROM liveindex WHERE id = %s AND symbol = %s", (user_id, symbol))
                shares = cursor.fetchone()
                return shares