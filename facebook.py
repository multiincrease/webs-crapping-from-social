import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import re
import csv
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys

def scrape_page(driver):
    """Extract details from the individual Facebook page"""
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    name_element = soup.select_one('div.x1e56ztr > span.x193iq5w > h1.x1heor9g')
    name = name_element.text.strip() if name_element else "Not found"
    
    email_element = soup.find('span', string=re.compile(r'\S+@\S+'))
    email = email_element.text.strip() if email_element else "Not found"

    phone_element = soup.find('span', string=re.compile(r'\+\d{1,3}\s\d{1,14}(\s\d{1,13})?'))
    phone = phone_element.text.strip() if phone_element else "Not found"
    
    return name, email, phone
def scrape(email, password, search_query):
    options = webdriver.ChromeOptions()
    prefs = {"profile.default_content_setting_values.notifications": 2}
    options.add_experimental_option("prefs", prefs)
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)

    # Login to Facebook
    driver.get("https://www.facebook.com/")
    driver.maximize_window()

    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'email'))).send_keys(email)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'pass'))).send_keys(password)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, 'login'))).click()
    except TimeoutException:
        print("Timeout while logging in.")
        driver.quit()
        return
    except Exception as e:
        print(f"Error logging in: {e}")
        driver.quit()
        return

    time.sleep(5)
    search_element = driver.find_element(By.XPATH, '//input[@placeholder="Search Facebook"]')
    search_element.send_keys(search_query + Keys.RETURN)
    time.sleep(5)

    # Navigate to the "Pages" tab after searching
    pages_tab = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//span[text()="Pages"]')))
    pages_tab.click()
    time.sleep(5)

    # # Extracting links from the search results
    # Extracting links from the search results
    link_elements = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'span.x193iq5w a[aria-hidden="true"]')))
    page_links = [element.get_attribute('href') for element in link_elements if "https://www.facebook.com/" in element.get_attribute('href')]
    valid_links = list(filter(None, page_links))  # Removing None values
  # Removing None values
  # Removing None values

    collected_data = []

    # Navigate to each link and extract data
    for link in valid_links:
        try:
            driver.get(link)
            time.sleep(5)
            print("Success:", link) 
            data = scrape_page(driver)
            collected_data.append(data)
            time.sleep(2)
        except Exception as e:
            print(f"Error processing link {link}. Error: {e}")

    driver.quit()
    return collected_data


def save_to_csv(data, filename):
    with open(filename, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Name", "Email", "Phone"])  # Add other headers
        writer.writerows(data)



# # # Example Usage
# data = scrape("7780633944", "Hemanth@569", "somalia companies")
# save_to_csv(data, 'facebook_data.csv')
