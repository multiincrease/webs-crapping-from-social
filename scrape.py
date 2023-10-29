import csv
import time
import re
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import urlsplit
from collections import deque

class GoogleMapScraper:
    def __init__(self):
        self.output_file_name = "googlemap_data.csv"
        self.headless = False
        self.driver = None
        self.unique_check = []

    def config_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")  # This ensures browser runs in the background
        driver = webdriver.Chrome(service=Service(ChromeDriverManager("114.0.5735.90").install()), options=options)
        self.driver = driver


    def save_data(self, data):
        header = ['Company Name', 'Address', 'Category', 'Phone', 'Website', 'Email']
        with open(self.output_file_name, 'a', newline='', encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=header)
            if data["Company Name"] not in self.unique_check:
                writer.writerow(data)
                self.unique_check.append(data["Company Name"])

    def get_email_from_website(self, url):
        emails = set()  
        unscraped = deque([url])  
        scraped = set()

        while len(unscraped):
            url = unscraped.popleft()  
            scraped.add(url)
        
            parts = urlsplit(url)
            base_url = "{0.scheme}://{0.netloc}".format(parts)
            if '/' in parts.path:
                path = url[:url.rfind('/')+1]
            else:
                path = url

            try:
                response = requests.get(url)
            except (requests.exceptions.MissingSchema, requests.exceptions.ConnectionError):
                continue
            
            new_emails = set(re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.com", response.text, re.I))
            emails.update(new_emails)
            
            soup = BeautifulSoup(response.text, 'lxml')
            
            for anchor in soup.find_all("a"):
                if "href" in anchor.attrs:
                    link = anchor.attrs["href"]
                else:
                    link = ''
                    
                    if link.startswith('/'):
                        link = base_url + link
                    elif not link.startswith('http'):
                        link = path + link
                    
                    if not link.endswith(".gz"):
                        if not link in unscraped and not link in scraped:
                            unscraped.append(link)

        return ', '.join(emails)

# Other functions here...



    def parse_contact(self, business):
        try:
            contact = business.find_elements(By.CLASS_NAME, "W4Efsd")[3].text.split("·")[-1].strip()
        except:
            contact = ""
        return contact

    # def parse_rating_and_review_count(self, business):
    #     try:
    #         reviews_block = business.find_element(By.CLASS_NAME, 'AJB7ye').text.split("(")
    #         rating = reviews_block[0].strip()
    #         reviews_count = reviews_block[1].split(")")[0].strip()
    #     except:
    #         rating = ""
    #         reviews_count = ""
    #     return rating, reviews_count

    def parse_address_and_category(self, business):
        try:
            address_block = business.find_elements(By.CLASS_NAME, "W4Efsd")[2].text.split("·")
            if len(address_block) >= 2:
                address = address_block[1].strip()
                category = address_block[0].strip()
            elif len(address_block) == 1:
                address = ""
                category = address_block[0]
        except:
            address = ""
            category = ""
        return address, category

    def get_business_info(self):
        time.sleep(2)
        for business in self.driver.find_elements(By.CLASS_NAME, 'THOPZb'):
            name = business.find_element(By.CLASS_NAME, 'fontHeadlineSmall').text
            # rating, reviews_count = self.parse_rating_and_review_count(business)
            address, category = self.parse_address_and_category(business)
            contact = self.parse_contact(business)
            try:
                website = business.find_element(By.CLASS_NAME, "lcr4fd").get_attribute("href")
            except NoSuchElementException:
                website = ""
            email = self.get_email_from_website(website)
            data = {"Company Name": name, "Address": address, "Category": category, "Phone": contact, "Website": website, "Email": email}
            self.save_data(data)

    def load_companies(self, search_term):
        base_url = "https://www.google.com/maps/search/"
        url = f"{base_url}{search_term.replace(' ', '+')}/"
        print("Getting business info", url)
        print("Getting business info", url)
        self.driver.get(url)
        time.sleep(5)
        panel_xpath = '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[1]'
        scrollable_div = self.driver.find_element(By.XPATH, panel_xpath)
        flag = True
        i = 0
        while flag:
            print(f"Scrolling to page {i + 2}")
            self.driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', scrollable_div)
            time.sleep(2)
            if "You've reached the end of the list." in self.driver.page_source:
                flag = False
            self.get_business_info()
            i += 1


# if __name__ == '__main__':
#     # Prompt user for the search term
#     search_term = input("Enter the search term for Google Maps: ").strip()

#     business_scraper = GoogleMapScraper()
#     business_scraper.config_driver()
#     business_scraper.load_companies(search_term)

