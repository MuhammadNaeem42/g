import os
import json
import sys
import pkg_resources
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import random
import logging
import time
import unicodedata
import dateparser
import datetime
import re


#setup logging
logging.basicConfig(filename='get_odds.log', level=logging.DEBUG, format='%(asctime)s %(message)s')

# Load environment variables from .env file
from dotenv import load_dotenv

load_dotenv()

# Debug: Check Python path and installed packages
print(sys.path)
print([pkg.key for pkg in pkg_resources.working_set])
logging.info(sys.path)
logging.info([pkg.key for pkg in pkg_resources.working_set])

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.705.63 Safari/537.36 Edg/88.0.705.63",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.192 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.705.63 Safari/537.36 Edg/88.0.705.63",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 OPR/107.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.3",
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 Edg/109.0.1518.14",
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.3",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 OPR/95.0.0.",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115."
]

# Ensure the logs directory exists
logs_dir = 'logs'
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

# Logging Configuration
log_file_path = os.path.join(logs_dir, 'get_odds.log')
logging.basicConfig(filename=log_file_path, level=logging.DEBUG, format='%(asctime)s %(message)s')


def get_ufc_matches():

    options = webdriver.ChromeOptions()
    user_agent = random.choice(USER_AGENTS)
    options.add_argument(f'user-agent={user_agent}')
    options.add_argument("--headless")  # Run Chrome in headless mode
    options.add_argument("--no-sandbox")  # Disable the sandbox
    options.add_argument("--disable-dev-shm-usage")  # Disable /dev/shm usage
    options.add_argument("--disable-gpu")  # Disable GPU usage
    options.add_argument("--window-size=1920x1080")  # Set window size

    driver = webdriver.Remote(
        command_executor='http://selenium_hub:4444/wd/hub',
        options=options
    )
    try:
        menus = driver.find_elements(By.CSS_SELECTOR, '.MuiPaper-root.MuiMenu-paper.MuiPopover-paper.MuiPaper-elevation8.MuiPaper-rounded')
        format_menu = menus[0]
        format_menu.click()

        decimal_option = driver.find_element(By.CSS_SELECTOR, "li[data-value='decimal']")
        decimal_option.click()
        time.sleep(1)
    except Exception as e:
        logging.error(f'Error: {e}')


    try:
        # Target URL
        url = 'https://fightodds.io/'
        driver.get(url)
        time.sleep(5)  # Wait for 5 seconds to ensure the page has loaded

        try:
            menus = driver.find_elements(By.CSS_SELECTOR, '[class*="MuiInputBase-root"][class*="MuiInput-root"][class*="MuiInput-underline"][class*="jss"][class*="MuiInputBase-formControl"][class*="MuiInput-formControl"]')
            format_menu = menus[0]
            format_menu.click()

            decimal_option = driver.find_element(By.CSS_SELECTOR, "li[data-value='decimal']")
            decimal_option.click()
            time.sleep(10)
        except Exception as e:
            print(f'Error: {e}')
            logging.error(f'Error: {e}')
            driver.quit()

        # dictionary called matches
        events = {}

        # find elements with the specified class name
        events_on_page = driver.find_elements(By.CSS_SELECTOR, '[class*="MuiButtonBase-root"][class*="MuiListItem-root"][class*="MuiListItem-dense"][class*="MuiListItem-gutters"][class*="MuiListItem-button"][class*="jss"]')

        # within each element, if p tag 'MuiTypography-root jss1575 MuiTypography-body1' text contains 'UFC', add to dictionary as event
        ufc_events = []
        for event in events_on_page:
            if 'RUFC' != event.text and 'UFC' in event.text:
                ufc_events.append(event)
        
        capped_events = ufc_events[:3]
        first_event = capped_events[1]
        for event in capped_events:
            time.sleep(5)
            if event.text == 'UFC':
                continue
            else:
                if event.text == first_event.text:
                    time.sleep(3)
                    event_text = event.find_element(By.CSS_SELECTOR, '[class*="MuiTypography-root"][class*="jss"][class*="MuiTypography-body1"]').text

                    print(f"Event: {event_text}")
                    logging.info(f"Event: {event_text}")
                    event_matches = driver.find_elements(By.CSS_SELECTOR, '[class*="MuiPaper-root"][class*="jss"][class*="MuiPaper-elevation0"]')
                    print("Found matches within event")

                    event_matches_list = []

                    for match in event_matches:
                        time.sleep(3)
                        table_body = match.find_element(By.CSS_SELECTOR, 'tbody.MuiTableBody-root')
                        table_rows = table_body.find_elements(By.CSS_SELECTOR, 'tr.MuiTableRow-root')
                        # the first two table rows are one match, the second two table rows are another match, and so on

                        # Iterate through every two rows together
                        for i in range(0, len(table_rows), 2):
                            row_a = table_rows[i]
                            row_b = table_rows[i+1]

                            fighter_attributes_a = row_a.find_elements(By.CSS_SELECTOR, 'td.MuiTableCell-root.MuiTableCell-body')
                            fighter_attributes_b = row_b.find_elements(By.CSS_SELECTOR, 'td.MuiTableCell-root.MuiTableCell-body')

                            # Initialize details dictionary for the current match
                            match_details_dict = {}

                            fighter_name_a = unicodedata.normalize('NFKD', fighter_attributes_a[0].text)
                            fighter_name_b = unicodedata.normalize('NFKD', fighter_attributes_b[0].text)     
                            bol_odds_a = unicodedata.normalize('NFKD', fighter_attributes_a[1].text)
                            bol_odds_b = unicodedata.normalize('NFKD', fighter_attributes_b[1].text)
                            dk_odds_a = unicodedata.normalize('NFKD', fighter_attributes_a[7].text)
                            dk_odds_b = unicodedata.normalize('NFKD', fighter_attributes_b[7].text)
                            fd_odds_a = unicodedata.normalize('NFKD', fighter_attributes_a[8].text)
                            fd_odds_b = unicodedata.normalize('NFKD', fighter_attributes_b[8].text)

                            
                            # Append match details to the list
                            match_details_dict = {
                                "fighter_name_a": fighter_name_a,
                                "fighter_name_b": fighter_name_b,
                                "bol_odds_a": bol_odds_a,
                                "bol_odds_b": bol_odds_b,
                                "dk_odds_a": dk_odds_a,
                                "dk_odds_b": dk_odds_b,
                                "fd_odds_a": fd_odds_a,
                                "fd_odds_b": fd_odds_b
                            }
                            event_matches_list.append(match_details_dict)
                    
                    # Add the list of match details to the event dictionary
                    events[event_text] = event_matches_list
                            
                elif event.text != first_event.text:
                    event.click()
                    time.sleep(3)
                    event_text = event.find_element(By.CSS_SELECTOR, '[class*="MuiTypography-root"][class*="jss"][class*="MuiTypography-body1"]').text

                    print(f"Event: {event_text}")
                    logging.info(f"Event: {event_text}")

                    event_matches = driver.find_elements(By.CSS_SELECTOR, '[class*="MuiPaper-root"][class*="jss"][class*="MuiPaper-elevation0"]')
                    print("Found matches within event")

                    event_matches_list = []

                    for match in event_matches:
                        time.sleep(3)
                        table_body = match.find_element(By.CSS_SELECTOR, 'tbody.MuiTableBody-root')
                        table_rows = table_body.find_elements(By.CSS_SELECTOR, 'tr.MuiTableRow-root')
                        # the first two table rows are one match, the second two table rows are another match, and so on

                        # Iterate through every two rows together
                        for i in range(0, len(table_rows), 2):
                            row_a = table_rows[i]
                            row_b = table_rows[i+1]

                            fighter_attributes_a = row_a.find_elements(By.CSS_SELECTOR, 'td.MuiTableCell-root.MuiTableCell-body')
                            fighter_attributes_b = row_b.find_elements(By.CSS_SELECTOR, 'td.MuiTableCell-root.MuiTableCell-body')

                            # Initialize details dictionary for the current match
                            match_details_dict = {}

                            fighter_name_a = unicodedata.normalize('NFKD', fighter_attributes_a[0].text)
                            fighter_name_b = unicodedata.normalize('NFKD', fighter_attributes_b[0].text)     
                            bol_odds_a = unicodedata.normalize('NFKD', fighter_attributes_a[1].text)
                            bol_odds_b = unicodedata.normalize('NFKD', fighter_attributes_b[1].text)
                            dk_odds_a = unicodedata.normalize('NFKD', fighter_attributes_a[7].text)
                            dk_odds_b = unicodedata.normalize('NFKD', fighter_attributes_b[7].text)
                            fd_odds_a = unicodedata.normalize('NFKD', fighter_attributes_a[8].text)
                            fd_odds_b = unicodedata.normalize('NFKD', fighter_attributes_b[8].text)

                            
                            # Append match details to the list
                            match_details_dict = {
                                "fighter_name_a": fighter_name_a,
                                "fighter_name_b": fighter_name_b,
                                "bol_odds_a": bol_odds_a,
                                "bol_odds_b": bol_odds_b,
                                "dk_odds_a": dk_odds_a,
                                "dk_odds_b": dk_odds_b,
                                "fd_odds_a": fd_odds_a,
                                "fd_odds_b": fd_odds_b
                            }
                            event_matches_list.append(match_details_dict)
                    
                    # Add the list of match details to the event dictionary
                    events[event_text] = event_matches_list
                else:
                    print("No events found")
                    break

        logging.info(events)
        return events            
    except Exception as e:
        print("An error occurred:", e)

    finally:
        driver.quit()

def add_event_date(events):
    # Get the current year
    current_year = datetime.datetime.now().year

    # Iterate over the dictionary
    for event, matches in events.items():
        # Extract the date string from the event string
        date_string = event.split(" ")[-2:]

        # Add the current year to the date string
        date_string.append(str(current_year))

        # Parse the date
        date = dateparser.parse(" ".join(date_string))

        # Format the date as YYYY-MM-DD
        formatted_date = date.strftime('%Y-%m-%d')

        # Add the formatted date to every match within the event
        for match in matches:
            match['event_date'] = formatted_date

    return events

def convert_to_prob(events):
    for event, matches in events.items():
        for match in matches:
            bol_odds_a_str = match.get("bol_odds_a", "")  # Get the value or set to empty string if not present
            bol_odds_b_str = match.get("bol_odds_b", "")  # Get the value or set to empty string if not present
            dk_odds_a_str = match.get("dk_odds_a", "")  # Get the value or set to empty string if not present
            dk_odds_b_str = match.get("dk_odds_b", "")  # Get the value or set to empty string if not present
            fd_odds_a_str = match.get("fd_odds_a", "")  # Get the value or set to empty string if not present
            fd_odds_b_str = match.get("fd_odds_b", "")  # Get the value or set to empty string if not present

            if bol_odds_a_str:
                bol_odds_a = float(bol_odds_a_str)
            else:
                bol_odds_a = None
            
            if bol_odds_b_str:
                bol_odds_b = float(bol_odds_b_str)
            else:
                bol_odds_b = None
            
            if dk_odds_a_str:
                dk_odds_a = float(dk_odds_a_str)
            else:
                dk_odds_a = None
            
            if dk_odds_b_str:
                dk_odds_b = float(dk_odds_b_str)
            else:
                dk_odds_b = None

            if fd_odds_a_str:
                fd_odds_a = float(fd_odds_a_str)
            else:
                fd_odds_a = None
            
            if fd_odds_b_str:
                fd_odds_b = float(fd_odds_b_str)
            else:
                fd_odds_b = None

            # convert odds to probabilities

            if bol_odds_a is not None:
                bol_prob_a = 1 / bol_odds_a
                match['bol_prob_a'] = round(bol_prob_a,2)
            else:
                match['bol_prob_a'] = None
            
            if bol_odds_b is not None:
                bol_prob_b = 1 / bol_odds_b
                match['bol_prob_b'] = round(bol_prob_b,2)
            else:
                match['bol_prob_b'] = None

            if dk_odds_a is not None:
                dk_prob_a = 1 / dk_odds_a
                match['dk_prob_a'] = round(dk_prob_a,2)
            else:
                match['dk_prob_a'] = None

            if dk_odds_b is not None:
                dk_prob_b = 1 / dk_odds_b
                match['dk_prob_b'] = round(dk_prob_b,2)
            else:
                match['dk_prob_b'] = None
            
            if fd_odds_a is not None:
                fd_prob_a = 1 / fd_odds_a
                match['fd_prob_a'] = round(fd_prob_a,2)
            else:
                match['fd_prob_a'] = None

            if fd_odds_b is not None:
                fd_prob_b = 1 / fd_odds_b
                match['fd_prob_b'] = round(fd_prob_b,2)
            else:
                match['fd_prob_b'] = None

    return events

def clean_event_title(events):
    cleaned_events = {}  # Create a new dictionary to store cleaned titles
    for event, matches in events.items():
        # Check if 'vs.' is in the event title
        if "vs." in event:
            # Take everything before "vs." and remove trailing whitespace
            cleaned_title = event.split("vs.")[0].strip() + " vs. " + event.split("vs.")[1].strip().split()[0]
        else:
            # If 'vs.' does not exist, take everything before the first date or extra information
            cleaned_title = event.split(':')[0].strip()

        cleaned_events[cleaned_title] = matches  # Add the matches under the cleaned or original title
    return cleaned_events



def get_and_format_events():
    events = get_ufc_matches()
    events = add_event_date(events)
    events = convert_to_prob(events)
    events = clean_event_title(events)
    
    # Save events to a JSON file
    with open('scraped_events.json', 'w') as f:
        json.dump(events, f)
    
    # Write status file indicating completion
    with open('scrape_complete.status', 'w') as f:
        f.write('completed')
    
    return events

if __name__ == "__main__":
    get_and_format_events()

