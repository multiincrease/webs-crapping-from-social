from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import re
import csv
from selenium.webdriver.common.keys import Keys
def twitter_login(driver, email, password):
    driver.get("https://twitter.com/login")

    try:
        # 2. Locate username/email field and input the value
        username_field = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.NAME, 'text'))  # 'text' should be the name attribute of the username input
        )
        username_field.send_keys(email)
        # Locate and click the "Next" button using the unique combination of class names
        # Locate and click the "Next" button using the unique combination of class names for the provided button
        next_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "div[role='button'][tabindex='0'].css-18t94o4.css-1dbjc4n.r-sdzlij.r-1phboty.r-rs99b7.r-ywje51.r-usiww2.r-2yi16.r-1qi8awa.r-1ny4l3l.r-ymttw5.r-o7ynqc.r-6416eg.r-lrvibr.r-13qz1uu"))
        )
        next_button.click()
        # 3. Locate the password field and input the value (assuming a name attribute of 'password' for this example)
        password_field = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.NAME, 'password')) 
        )
        password_field.send_keys(password)

        # Click the "Log in" button
        login_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "div[role='button'][data-testid='LoginForm_Login_Button']"))
        )
        login_button.click()

        # 5. (Optional) Verify if the login was successful, by checking for a specific element or URL
        # Here's a simple URL check as an example:
        
    except Exception as e:
        print(f"Error during login: {e}")
def extract_information_from_twitter_search(driver, search_query):
    base_url = "https://twitter.com/explore"  # This is Twitter's search page
    driver.get(base_url)

    try:
        # Locate the search box using the provided `data-testid` attribute
        search_box = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[data-testid='SearchBox_Search_Input']"))
        )

        # Input the search query and press the "Enter" key
        search_box.send_keys(search_query)
        search_box.send_keys(Keys.RETURN)

        # Assuming a single profile is what you're interested in. Adjust this if needed.
        profile_element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.css-1dbjc4n.r-1loqt21.r-18u37iz.r-1wbh5a2 a')))
        profile_url = profile_element.get_attribute('href')

        if profile_url:
            extract_information_from_twitter(driver, profile_url)
        else:
            print("Profile not found.")
    except Exception as e:
        print(f"Error during search: {e}")


def extract_information_from_twitter(url):
    options = webdriver.ChromeOptions()
    #options.add_argument("--headless")
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

# User inputs
email = "hemanth131099@gmail.com"
password = "Hemanth@569"
query = "somalia compalies"

options = webdriver.ChromeOptions()
#options.add_argument("--headless")
with webdriver.Chrome(options=options) as driver:
    if twitter_login(driver, email, password):
        extract_information_from_twitter_search(driver, query)

