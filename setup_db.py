import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database connection parameters
db_name = os.getenv('DB_NAME')
db_user = os.getenv('DB_USERNAME')
db_password = os.getenv('DB_PASSWORD')
db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')

# Connection string
conn_str = f"dbname='{db_name}' user='{db_user}' password='{db_password}' host='{db_host}' port='{db_port}'"

# SQL to create the table
create_table_sql = """
CREATE TABLE IF NOT EXISTS fight_odds_io_ufc (
    id SERIAL PRIMARY KEY,
    event VARCHAR(255),
    event_date DATE,
    fighter_name_a VARCHAR(255),
    fighter_name_b VARCHAR(255),
    bol_odds_a FLOAT,
    bol_odds_b FLOAT,
    dk_odds_a FLOAT,
    dk_odds_b FLOAT,
    fd_odds_a FLOAT,
    fd_odds_b FLOAT,
    bol_prob_a FLOAT,
    bol_prob_b FLOAT,
    dk_prob_a FLOAT,
    dk_prob_b FLOAT,
    fd_prob_a FLOAT,
    fd_prob_b FLOAT,
    scraped_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

# Connect to the database and create the table
try:
    conn = psycopg2.connect(conn_str)
    cur = conn.cursor()
    cur.execute(create_table_sql)
    conn.commit()
    cur.close()
    conn.close()
    print("Table created successfully")
except psycopg2.Error as e:
    print(f"Error creating table: {e}")
