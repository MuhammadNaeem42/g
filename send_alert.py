import logging
import psycopg2
import os
from dotenv import load_dotenv

logging.basicConfig(filename='steam_alert.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()
db_name = os.getenv('DB_NAME')
db_user = os.getenv('DB_USERNAME')
db_password = os.getenv('DB_PASSWORD')
db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')

# Connection string
db_path = f"dbname='{db_name}' user='{db_user}' password='{db_password}' host='{db_host}' port='{db_port}'"

def most_recent_prob(db_path):
    conn = psycopg2.connect(db_path)
    cur = conn.cursor()
    cur.execute('''
        SELECT scraped_time, event, fighter_name_a, fighter_name_b, bol_prob_a, bol_prob_b, dk_prob_a, dk_prob_b, fd_prob_a, fd_prob_b 
        FROM fight_odds_io_ufc
        WHERE scraped_time = (SELECT MAX(scraped_time) FROM fight_odds_io_ufc)
    ''')
    results = cur.fetchall()
    logging.info(f'most_recent_prob results: {results}')
    conn.close()
    return results

def second_most_recent_prob(db_path):
    conn = psycopg2.connect(db_path)
    cur = conn.cursor()
    # First, get the list of unique scraped_times, ordered from most to least recent
    cur.execute('''
        SELECT DISTINCT scraped_time FROM fight_odds_io_ufc
        ORDER BY scraped_time DESC
    ''')
    times = cur.fetchall()
    
    # If there are at least two distinct scraped_times, proceed to fetch the second most recent
    if len(times) >= 2:
        second_most_recent_time = times[1][0]  # Get the second most recent time
        cur.execute('''
            SELECT scraped_time, event, fighter_name_a, fighter_name_b, bol_prob_a, bol_prob_b, dk_prob_a, dk_prob_b, fd_prob_a, fd_prob_b
            FROM fight_odds_io_ufc
            WHERE scraped_time = %s
        ''', (second_most_recent_time,))
        results = cur.fetchall()
        logging.info(f'second_most_recent_prob results: {results}')
    else:
        results = []
        logging.info('Not enough data for second_most_recent_prob')

    conn.close()
    return results


def compare_probs(most_recent, second_most_recent):
    comparison_results = []
    for i in range(len(most_recent)):
        if most_recent[i] is None or second_most_recent[i] is None:
            # Handle case where either most_recent or second_most_recent is None
            comparison_result = [None, None, None, None, None]
        else:
            comparison_result = []
            # Add event details (indices 0 and 1)
            comparison_result.extend(most_recent[i][:4])
            for j in range(4, 7):  # Indexes 4, 5, 6 correspond to bol_prob_a, dk_prob_a, fd_prob_a
                most_recent_value = most_recent[i][j]
                second_most_recent_value = second_most_recent[i][j]
                if most_recent_value is not None and second_most_recent_value is not None:
                    diff = second_most_recent_value - most_recent_value
                else:
                    diff = None
                comparison_result.append(diff)
        comparison_results.append(comparison_result)
    logging.info(f'comparison_results: {comparison_results}')
    return comparison_results


def check_comparison_results(comparison_results):
    filtered_results = []
    for result in comparison_results:
        if result[4] is not None and result[5] is not None and result[6] is not None:
            #if round(abs(result[4]),2) > 0.03 or round(abs(result[5],2)) > 0.03 or round(abs(result[6]),2) > 0.03:
            if round(abs(result[4]), 2) > 0.03 or round(abs(result[5]), 2) > 0.03 or round(abs(result[6]), 2) > 0.03:
                filtered_results.append(result[:6])
    if not filtered_results:
        logging.info('No significant steam detected')
        print('No significant steam detected')
    logging.info(f'filtered_results: {filtered_results}')
    return filtered_results

def decipher_filtered_results(filtered_results):
    for result in filtered_results:
        scraped_time = result[0]
        event = result[1]
        fighter_a = result[2]
        fighter_b = result[3]
        diff_a = result[4]
        diff_b = result[5]
    
    cleaned_results = []

    if diff_a > 0:
        cleaned_results.append(f'At {event}, {fighter_a} has steamed {abs(diff_a)}.')
    elif diff_b > 0:
        cleaned_results.append(f'At {event}, {fighter_b} has steamed {abs(diff_b)}.')
    return cleaned_results



import smtplib
from email.mime.text import MIMEText

def send_email(cleaned_results):
    sender_email = 'weickertdane99@gmail.com'
    receiver_email = 'combat.notifications.inbox@gmail.com'
    subject = 'UFC Steam Alert!'
    body = '\n'.join(str(result) for result in cleaned_results)

    message = MIMEText(body)
    message['Subject'] = subject
    message['From'] = sender_email
    message['To'] = receiver_email

    try:
        smtp_obj = smtplib.SMTP('smtp.gmail.com', 587)
        smtp_obj.starttls()
        smtp_obj.login(sender_email, 'ltgrpalqlinmpvxf')
        smtp_obj.sendmail(sender_email, receiver_email, message.as_string())
        smtp_obj.quit()
        print('Email sent successfully!')
    except smtplib.SMTPException as e:
        print('Error sending email:', str(e))


def main():
    #db_path = "dbname='{db_name}' user='{db_user}' password='{db_password}' host='{db_host}' port='{db_port}'"
    most_recent = most_recent_prob(db_path)
    second_most_recent = second_most_recent_prob(db_path)
    comparison_results = compare_probs(most_recent, second_most_recent)
    filtered_results = check_comparison_results(comparison_results)
    # Ensure decipher_filtered_results is called to define cleaned_results
    if filtered_results:
        cleaned_results = decipher_filtered_results(filtered_results)
        send_email(cleaned_results)


if __name__ == "__main__":
    main()
