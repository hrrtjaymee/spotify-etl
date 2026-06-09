import psycopg2
from dotenv import load_dotenv
import os
from src.utils.logger import get_logger

load_dotenv()
logger = get_logger(__name__)

def get_connection():
    try: 
        conn = psycopg2.connect(
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT'),
            database=os.getenv('DB_NAME')
            )
        logger.info('Database connected successfully')
    except Exception as e: 
        logger.critical(f'Database not connected successfully {e}')
    return conn
