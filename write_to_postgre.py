import json
import psycopg2
from psycopg2 import sql
import os
from dotenv import load_dotenv
import logging
import time

# Ensure the logs directory exists
logs_dir = 'logs'
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

# Logging Configuration
log_file_path = os.path.join(logs_dir, 'write_to_postgre.log')
logging.basicConfig(filename=log_file_path, level=logging.DEBUG, format='%(asctime)s %(message)s')


# Polling interval (seconds)
POLL_INTERVAL = 5
# Timeout (seconds)
TIMEOUT = 300

def wait_for_data():
    start_time = time.time()
    while not os.path.exists('scrape_complete.status'):
        if time.time() - start_time > TIMEOUT:
            logging.error('Timeout waiting for scrape_complete.status')
            raise TimeoutError('Timeout waiting for scrape_complete.status')
        logging.info('Waiting for scrape_complete.status...')
        time.sleep(POLL_INTERVAL)
    logging.info('Found scrape_complete.status')

def read_scraped_data():
    with open('scraped_events.json', 'r') as f:
        events = json.load(f)
    return events

def write_scraped_odds_to_db(events):
    # PostgreSQL database connection parameters
    load_dotenv()
    db_name = os.getenv('DB_NAME')
    db_user = os.getenv('DB_USERNAME')
    db_password = os.getenv('DB_PASSWORD')
    db_host = os.getenv('DB_HOST')
    db_port = os.getenv('DB_PORT')

    # Print loaded environment variables for debugging
    print(f"DB_NAME: {db_name}")
    print(f"DB_USERNAME: {db_user}")
    print(f"DB_PASSWORD: {db_password}")
    print(f"DB_HOST: {db_host}")
    print(f"DB_PORT: {db_port}")

    # Connection string
    conn_str = f"dbname='{db_name}' user='{db_user}' password='{db_password}' host='{db_host}' port='{db_port}'"

    try:
        # Establish a connection to the PostgreSQL database
        conn = psycopg2.connect(conn_str)
        logging.info(f"Connected to {db_name}")
        print(f"Connected to {db_name}")

        # Create a cursor object
        cur = conn.cursor()

        # Inside your loop where you execute the INSERT statement
        for event, fights in events.items():
            for fight in fights:
                # Replace empty strings with None for all numeric fields
                values_to_insert = (
                    event, 
                    fight['event_date'], 
                    fight['fighter_name_a'], 
                    fight['fighter_name_b'],
                    None if fight['bol_odds_a'] == '' else fight['bol_odds_a'],
                    None if fight['bol_odds_b'] == '' else fight['bol_odds_b'],
                    None if fight['dk_odds_a'] == '' else fight['dk_odds_a'],
                    None if fight['dk_odds_b'] == '' else fight['dk_odds_b'],
                    None if fight['fd_odds_a'] == '' else fight['fd_odds_a'],
                    None if fight['fd_odds_b'] == '' else fight['fd_odds_b'],
                    None if fight['bol_prob_a'] == '' else fight['bol_prob_a'],
                    None if fight['bol_prob_b'] == '' else fight['bol_prob_b'],
                    None if fight['dk_prob_a'] == '' else fight['dk_prob_a'],
                    None if fight['dk_prob_b'] == '' else fight['dk_prob_b'],
                    None if fight['fd_prob_a'] == '' else fight['fd_prob_a'],
                    None if fight['fd_prob_b'] == '' else fight['fd_prob_b']
                )

                cur.execute(sql.SQL('''
                    INSERT INTO fight_odds_io_ufc (event, event_date, fighter_name_a, fighter_name_b, bol_odds_a, bol_odds_b, dk_odds_a, dk_odds_b, fd_odds_a, fd_odds_b, bol_prob_a, bol_prob_b, dk_prob_a, dk_prob_b, fd_prob_a, fd_prob_b, scraped_time)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, now())
                '''), values_to_insert)

        # Commit the changes and close the connection
        conn.commit()
        cur.close()
        conn.close()

    except psycopg2.Error as e:
        logging.error(f"Failed to connect to {db_name}: {e}")
        print(f"Failed to connect to {db_name}: {e}")
        return  # Early return to exit the function if connection fails

def main():
    wait_for_data()
    events = read_scraped_data()
    write_scraped_odds_to_db(events)

if __name__ == "__main__":
    main()