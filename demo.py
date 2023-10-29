import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import csv
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
from selenium.common.exceptions import TimeoutException
def find_elements_with_retry(driver, by, value, retries=3, delay=5):
    for i in range(retries):
        try:
            return WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((by, value)))
        except TimeoutException:
            if i < retries - 1:  # i is zero indexed
                print(f"Attempt {i+1} failed. Retrying after {delay} seconds.")
                time.sleep(delay)
            else:
                print("Max retries reached.")
                raise


def scrape_instagram(query, email, password,limit=10):
    options = webdriver.ChromeOptions()
    #options.add_argument("--headless")
    prefs = {"profile.default_content_setting_values.notifications": 2}
    options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(options=options)

    # Login to Instagram
    driver.get("https://www.instagram.com/accounts/login/")
    driver.maximize_window()

    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, 'username'))).send_keys(email)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, 'password'))).send_keys(password)
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//button[descendant::div[text()="Log in"]]'))).click()
    except TimeoutException:
        print("Timeout while logging in.")
        driver.quit()
        return
    except Exception as e:
        print(f"Error logging in: {e}")
        driver.quit()
        return

    time.sleep(5)
    
    # Navigate to the Instagram home page after login
    driver.get('https://www.instagram.com/')
    search_icon = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'svg[aria-label="Search"]')))
    search_icon.click()
    
    search_box = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[aria-label="Search input"]')))
    search_box.send_keys(query)
    time.sleep(2)  # Give some time for search results to populate
    search_results = find_elements_with_retry(driver, By.CSS_SELECTOR, 'a.x1i10hfl.x1qjc9v5.xjbqb8w.xjqpnuy.xa49m3k.xqeqjp1')
    # Printing the length of search results
    print(f"Total search results: {len(search_results)}")
    # Take the minimum of the user-specified limit or the actual search results found
    search_results = search_results[:min(limit, len(search_results))]

    profile_urls = [el.get_attribute('href') for el in search_results if 'explore/locations/' not in el.get_attribute('href') and 'explore/tags/' not in el.get_attribute('href')]
    # insta_elements = find_elements_with_retry(driver, By.CSS_SELECTOR, 'a.x1i10hfl.x1qjc9v5.xjbqb8w.xjqpnuy.xa49m3k.xqeqjp1')
    # profile_urls = [link.get_attribute('href') for link in insta_elements]
    # Initialization for CSV saving
    with open('instagram_data2.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Username", "Link", "Phone Number", "Email"])

        for profile_url in profile_urls:
            driver.get(profile_url)
            
            try:
                time.sleep(3)  # Give the profile page some time to load.
                # Wait for the username element to load
                WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h2.x1lliihq.x1plvlek.xryxfnj.x1n2onr6.x193iq5w.xeuugli.x1fj9vlw.x13faqbe.x1vvkbs.x1s928wv.xhkezso.x1gmr53x.x1cpjm7i.x1fgarty.x1943h6x.x1i0vuye.x1ms8i2q.xo1l8bm.x5n08af.x10wh9bi.x1wdrske.x8viiok.x18hxmgj')))

                # Get the page source
                page_source = driver.page_source

                # Parse the page source with BeautifulSoup
                soup = BeautifulSoup(page_source, 'html.parser')
                # Extract the username
                username_element = soup.find('h2', class_='x1lliihq x1plvlek xryxfnj x1n2onr6 x193iq5w xeuugli x1fj9vlw x13faqbe x1vvkbs x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x x1i0vuye x1ms8i2q xo1l8bm x5n08af x10wh9bi x1wdrske x8viiok x18hxmgj')
                username = username_element.text if username_element else None

                # Extract the link
                # Target the outer span first
                outer_span = soup.find('span', class_='x1lliihq x1plvlek xryxfnj x1n2onr6 x193iq5w xeuugli x1fj9vlw x13faqbe x1vvkbs x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x x1i0vuye xvs91rp x1s688f x7l2uk3 x10wh9bi x1wdrske x8viiok x18hxmgj')

                # Now, find the inner span within the outer span
                if outer_span:
                    inner_span = outer_span.find('span', class_='x1lliihq x193iq5w x6ikm8r x10wlt62 xlyipyv xuxw1ft')
                    link = inner_span.text if inner_span else None
                else:
                    link = None

                
                # If the link does not start with 'http' (covering both 'http' and 'https'), prepend it with 'https://'
                if link and not link.startswith('http'):
                    link = f"https://{link}"

                # Try navigating to the link and extracting phone and email
                phone_number = None
                email = None

                if link:
                    try:
                        driver.get(link)
                        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
                        body_text = driver.find_element(By.TAG_NAME,'body').text

                    # Phone number regex that checks for a '+' symbol followed by digits, possibly separated by spaces or hyphens.
                        phone_match = re.search(r'\+\d{1,3}\s\d{1,14}(\s\d{1,13})?', body_text)
                        phone_number = phone_match.group() if phone_match else None

                        # Email regex that checks for "@" and is more permissive of TLDs.
                        email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', body_text)

                    
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

            except Exception as e:
                print(f"Error while scraping profile {e}")
                username, link, phone_number, email = (None, None, None, None)
            # Save to CSV
            writer.writerow([username, link, phone_number, email])
            
            # Navigate back to the search results to process the next profile
            driver.back()

    driver.quit()
    
scrape_instagram("companies", "hemanth131099@gmail.com", "Hemanth@569",limit=5)        