import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

def get_connection():
    try: 
        conn = psycopg2.connect(
            database=os.getenv('DB_DEV'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT')
            )
        print('Database connected successfully')
    except Exception as e: 
        print('Database not connected successfully')
        print(e)
    return conn
