#Import required selenium modules
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
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
    except ( NoSuchElementException, TimeoutException, StaleElementReferenceException ):
        break

'''FIND LISTINGS AND STORE TO A LIST'''
#Finding the UL element containing all the search result items (as list items)
# listings_list = driver.find_element(By.CSS_SELECTOR, "#container > main > div > div > section > div > div > div:nth-child(6) > div._3etsg > div > div:nth-child(2) > ul")
car_listing_ul = None
all_uls = driver.find_elements(By.TAG_NAME, 'ul')
for uls in all_uls:
    if uls.get_attribute("data-aut-id") == "itemsList":
        car_listing_ul = uls

#Finding All list items (li) inside the UL list
listings = car_listing_ul.find_elements(By.TAG_NAME, "li")

#Initialize empty list to store scrapped data (for further writing on a csv file)
scraped_datas = []

#Loop through each list element (list item) and further find required info from their respective XPath
for listing in listings:
    if listing.get_attribute('data-aut-id') == 'itemBox':
        try:
            ad_link = listing.find_element(By.XPATH, "./a").get_attribute("href")
        except NoSuchElementException:
            print("No ad_link")
            break
        try:
            ad_details_card = listing.find_element(By.CLASS_NAME, "_31uw8")
        except NoSuchElementException:
            print("No ad_details")
        try:
            ad_price = ad_details_card.find_element(By.CSS_SELECTOR, "span[data-aut-id='itemPrice']").text
        except NoSuchElementException:
            print("No ad_price")
        try:
            ad_sub_title = ad_details_card.find_element(By.CSS_SELECTOR, "div[data-aut-id='itemSubTitle']").text.split(" - ")
            model_year = ad_sub_title[0]
            kms_driven = ad_sub_title[1]
        except NoSuchElementException:
            print("No ad_sub_title")
        try:
            ad_title = ad_details_card.find_element(By.CSS_SELECTOR, "div[data-aut-id='itemTitle']").get_attribute('title')
        except NoSuchElementException:
            print("No ad_title")
        try:
            ad_location = ad_details_card.find_element(By.CSS_SELECTOR, "div[data-aut-id='itemDetails']").text.split("\n")[0]
        except NoSuchElementException:
            print("No ad_title")    
        scraped_datas.append([ad_link, ad_price, model_year, kms_driven, ad_title, ad_location])

'''WRITE SCRAPED LIST TO CSV'''
search_query = input_url.split("/")[-1][2:] #extract the search query form the url
with open(f'scraped_data/{search_query}.csv', 'w', newline='', encoding="utf-8") as file: 
    writer = csv.writer(file)
    headers = ['Ad Link','Price','Model Year', 'KMS Driven', 'Ad Title', 'Ad Location']
    writer.writerow(headers)
    for data in scraped_datas:
        writer.writerow(data)
