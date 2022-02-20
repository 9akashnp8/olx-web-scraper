#Import required selenium modules
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

#Import webdriver_manager for easy management (auto-updation, global path) of driver executable
from webdriver_manager.chrome import ChromeDriverManager

import time #time for various wait/sleep functions
import csv #csv for storing the scraped data
import sys #sys for flushing the buffer (typing effect)

#Welcome message
print("OLX Web Scraper!")
welcome_message = ["Scrap for any item an olx.in.", "All you need to provide is the search link to scrap", 
"1. Go to olx.in and search the item", "2. Copy the queried url and provide it below"]

#typing effect for welcome message
for line in welcome_message: 
    for c in line:           
        print(c, end='')     
        sys.stdout.flush()
        time.sleep(0.03)
    print('')

#Collect the link to scrap from user
input_url = input("URL: ")

#Set chromedriver location (automated using webdriver-manager)
service = Service(executable_path=ChromeDriverManager().install())
#create a chrome webdriver instance
driver = webdriver.Chrome(service=service)
#navigate the browser instance to the input_url
driver.get(input_url)

while True:
    '''
    While loop to load all results for the search query by finding and clicking on the "Load More" button unless
    the button doesn't exist i.e., all results loaded, no more results to load. Without this, only the first 20 listings
    will be scraped
    '''
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@data-aut-id="btnLoadMore"]')))
        driver.find_element(By.XPATH, '//*[@data-aut-id="btnLoadMore"]').click()
        print("Clicked 'Load More'")
    except TimeoutException:
        break

'''FIND LISTINGS AND STORE TO A LIST'''
#Finding the UL element containing all the search result items (as list items)
listings_list = driver.find_element(By.CSS_SELECTOR, "#container > main > div > div > section > div > div > div:nth-child(6) > div._3etsg > div > div:nth-child(2) > ul")

#Finding All list items (li) inside the UL list
listings = listings_list.find_elements(By.CSS_SELECTOR, "li")

#Initialize empty list to store scrapped data (for further writing on a csv file)
scraped_datas = []

#Loop through each list element (list item) and further find required info from their respective XPath
for listing in listings:
    try:
        #Try method 1 for finding elements
        price = listing.find_element(By.XPATH, "./a/div/span[1]").text
        year_and_odo = listing.find_element(By.XPATH, "./a/div/span[2]").text
        short_description = listing.find_element(By.XPATH, "./a/div/span[3]").text
        location = listing.find_element(By.XPATH, "./a/div/div/span[1]").text
        date_published = listing.find_element(By.XPATH, "./a/div/div/span[2]").text
        listing_link = listing.find_element(By.XPATH, "./a")
        ad_link = listing_link.get_attribute('href')
        #Once data gathered, append them to the scraped_datas list
        scraped_datas.append([price, year_and_odo, short_description, location, date_published,ad_link])
    except NoSuchElementException:
        #If no results being found from method 1, try method 2. If no results found in method 2, pass
        try:
            price = listing.find_element(By.XPATH, "./a/div[1]/div[2]/span").text
            year_and_odo = listing.find_element(By.XPATH, "./a/div[1]/div[2]/div[1]").text
            short_description = listing.find_element(By.XPATH, "./a/div[1]/div[2]/div[2]").text
            location = listing.find_element(By.XPATH, "./a/div[1]/div[2]/div[3]").text
            date_published = listing.find_element(By.XPATH, "./a/div[1]/div[2]/div[3]/span").text
            listing_link = listing.find_element(By.XPATH, "./a")
            ad_link = listing_link.get_attribute('href')
            scraped_datas.append([price, year_and_odo, short_description, location, date_published,ad_link])
        except NoSuchElementException:
            pass
        pass

'''WRITE SCRAPED LIST TO CSV'''
search_query = input_url.split("/")[-1][2:] #extract the search query form the url
with open(f'scraped_data/{search_query}.csv', 'w', newline='', encoding="utf-8") as file: 
    writer = csv.writer(file)
    headers = ['Price','Detail','Description', 'Location', 'Date of Listing', 'Link']
    writer.writerow(headers)
    for data in scraped_datas:
        writer.writerow(data)
