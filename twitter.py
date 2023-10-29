from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import re
import csv

def construct_twitter_url_from_handle(handle):
    """Converts a Twitter handle to its corresponding URL."""
    base_twitter_url = "https://twitter.com/"
    return base_twitter_url + handle
def extract_information_from_twitter(url):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    driver.get(url)

   # Wait for an 'a' tag with the class 'css-4rbku5' to appear, which should indicate that tweets (and their links) are loaded
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a.css-4rbku5')))


    # Get the page source
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')

    # Extract the username
    username_element = soup.find('div', class_='css-1dbjc4n r-1awozwy r-18u37iz r-dnmrzs')
    if username_element:
        username_span = username_element.find('span', class_='css-901oao css-16my406 r-poiln3 r-bcqeeo r-qvutc0')
        if username_span:
            username = username_span.text 
            print(f"Username: {username}")
        else:
            print("Username not found.")
    else:
        print("Username element not found.")

    # Extract the link based on the provided structure
    link_element = soup.select_one('a[data-testid="UserUrl"]')
    
    if link_element:
        link = link_element['href']
        print(f"URL: {link}")

        display_text_element = link_element.select_one('span.css-901oao')
        if display_text_element:
            print(f"Display Text: {display_text_element.text}")
        else:
            print("Display text not found.")
    else:
        print("Link not found.")

    # If the link does not start with 'http' (covering both 'http' and 'https'), prepend it with 'https://'
    if link and not link.startswith('http'):
        link = f"https://{link}"    
    # Your added code
    phone_number = None
    email = None

    if link:
        try:
            driver.get(link)
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
            body_text = driver.find_element(By.TAG_NAME,'body').text

            phone_regex = r'\+\d{1,3}\s\d{1,14}(\s\d{1,13})?'

            phone_match = re.search(phone_regex, body_text)
            phone_number = phone_match.group() if phone_match else None


            email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            email_match = re.search(email_regex, body_text)
            email = email_match.group() if email_match else None


            if phone_number:
                print(f"Found Phone Number: {phone_number}")
            else:
                print("No phone number detected.")

            if email:
                print(f"Found Email: {email}")
            else:
                print("No email detected.")
        except Exception as e:
            print(f"An error occurred: {e}")

    driver.quit()
    # Save to CSV
    with open('twitter_data.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Username", "Link", "Phone Number", "Email"])
        writer.writerow([username, link, phone_number, email])

    print("Data saved to twitter_data.csv")
# Ask user for the Twitter handle
# handle = input("Enter the Twitter handle (without @): ").strip()
# url = construct_twitter_url_from_handle(handle)

# extract_information_from_twitter(url)
#GrabID
#iom_somalia
