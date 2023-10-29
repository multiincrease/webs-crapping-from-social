from facebook import scrape , save_to_csv
from scrape import GoogleMapScraper
from insta import scrape_instagram
from twitter import extract_information_from_twitter,construct_twitter_url_from_handle

def main():
    print("Choose the platform to scrape:")
    print("1. Google Maps")
    print("2. Facebook")
    print("3. Instagram")
    print("4. Twitter")
    choice = input("Enter your choice (1/2/3/4): ").strip()

    if choice == "1":
        # Replace this with your Google Maps scraping function
        search_term = input("Enter the search term for Google Maps: ").strip()
        business_scraper = GoogleMapScraper()
        business_scraper.config_driver()
        business_scraper.load_companies(search_term)
        # data = GoogleMapScraper(url)
        
    elif choice == "2":
        # Replace this with your Facebook scraping function
        email = input("Enter your Facebook email: ").strip()
        password = input("Enter your Facebook password: ").strip()
        search_query = input("Enter the Page name or query:").strip()
        data = scrape(email, password, search_query)
        save_to_csv(data, 'facebook_data1.csv')
    elif choice == "3":
        query = input("Enter the Instagram profile or query: ").strip()
        email = input("Enter your instagram email or phone number: ").strip()
        password = input("Enter your instagram password: ").strip()
        limit = int(input("enter the limit of pages to scrape:").strip())
        data = scrape_instagram(query, email, password,limit)
    elif choice == "4":
        handle = input("Enter the Twitter handle (without @): ").strip()
        url = construct_twitter_url_from_handle(handle)

        extract_information_from_twitter(url)

    else:
        print("Invalid choice.")

if __name__ == "__main__":
    main()