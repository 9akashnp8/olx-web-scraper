#Import required selenium modules
import math
from msilib.schema import Class
from multiprocessing.connection import wait
import random
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

class Scraper:
    load_dotenv()
    area_list = ['Jakarta D.K.I.', 'Jawa Barat', 'Jawa Timur', 'Banten', 'Jawa Tengah', 'Yogyakarta D.I.', 'Sumatra Selatan', 'Sumatra Utara', 'Kalimantan Selatan', 'Bali', 'Riau', 'Lampung', 'Sulawesi Selatan', 'Aceh D.I.', 'Sumatra Barat', 'Kalimantan Timur', 'Kalimantan Barat', 'Jambi', 'Kepulauan Riau', 'Nusa Tenggara Barat']
    brand_list = ['Toyota', 'Honda', 'Mercedes-Benz', 'Mitsubishi', 'Nissan', 'BMW', 'Suzuki', 'Daihatsu', 'Mazda', 'Lexus', 'Hyundai', 'Chevrolet', 'Datsun']
    scraped_datas = []
    #Link
    url = "https://www.olx.co.id"
    main_url = url+"/mobil-bekas_c198"
    initial_url = ''
    #Collect the data to scrap from user
    
    def __init__(self):
        self.input_area = sys.argv[1]
        self.input_brand = sys.argv[2]
        self.input_model = sys.argv[3]
        self.input_transmission = sys.argv[4]
        self.input_year = sys.argv[5]
        # self.input_area = input("Area (Jakarta, Banten, Jawa Timur) :")
        # self.input_brand = input("Brand ('Toyota', 'Honda', 'Mercedes-Benz', 'Mitsubishi', 'Nissan', 'BMW', 'Suzuki', 'Daihatsu', 'Mazda', 'Lexus', 'Hyundai', 'Chevrolet', 'Datsun') :")
        # self.input_model = input("Model (CR-V, HR-V, etc) :")
        # self.input_transmission = input("Transmission (automatic / manual) :")
        # self.input_year = input("Year (1994,2020) :")
        #Set chromedriver location (automated using webdriver-manager)
        chrome_opt = webdriver.ChromeOptions()

        chrome_opt.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2}) 
        chrome_opt.add_argument("--no-sandbox") 
        chrome_opt.add_argument("--disable-setuid-sandbox") 

        chrome_opt.add_argument("--remote-debugging-port=9222")  # this

        chrome_opt.add_argument("--disable-dev-shm-using") 
        chrome_opt.add_argument("--disable-extensions") 
        chrome_opt.add_argument("--disable-gpu") 
        chrome_opt.add_argument("start-maximized") 
        chrome_opt.add_argument("disable-infobars")
        chrome_opt.add_argument(r"user-data-dir=.\cookies\\test") 

        self.service = Service(executable_path=ChromeDriverManager().install())
        #create a chrome webdriver instance
        self.driver = webdriver.Chrome(service=self.service, chrome_options=chrome_opt)
        self.db_init()
    
    def db_init(self):
        self.connection = psycopg2.connect(user=os.getenv("DB_USER"),
                                  password=os.getenv("DB_PASSWORD"),
                                  host=os.getenv("DB_HOST"),
                                  port=os.getenv("DB_PORT"),
                                  database=os.getenv("DB_DATABASE"))
        self.cursor = self.connection.cursor()

#typing effect for welcome message
for line in welcome_message: 
    for c in line:           
        print(c, end='')     
        sys.stdout.flush()
        time.sleep(0.03)
    print('')

#Link
url = "https://www.olx.co.id"
main_url = url+"/mobil-bekas_c198"

#Collect the data to scrap from user
input_area = input("Area (Jakarta, Banten, Jawa Timur) :")
input_brand = input("Brand ('Toyota', 'Honda', 'Mercedes-Benz', 'Mitsubishi', 'Nissan', 'BMW', 'Suzuki', 'Daihatsu', 'Mazda', 'Lexus', 'Hyundai', 'Chevrolet', 'Datsun') :")
input_model = input("Model (CR-V, HR-V, etc) :")
input_transmission = input("Transmission (automatic / manual) :")
input_year = input("Year (1994,2020) :")

#Set data according to list
area = list(filter(lambda a: input_area.capitalize() in a, area_list))[0]
# print("area is :" + area[0])
brand = list(filter(lambda b: input_brand.capitalize() in b, brand_list))[0]
model = input_model
transmission = 'manual' if input_transmission.lower() == 'manual' else 'automatic'
year = input_year

print(f'INPUT : {area} - {brand} - {model} - {transmission} - {year}')

#Set chromedriver location (automated using webdriver-manager)
service = Service(executable_path=ChromeDriverManager().install())
#create a chrome webdriver instance
driver = webdriver.Chrome(service=service)
'''https://www.olx.co.id/jakarta-selatan_g4000030/mobil-bekas_c198
?filter=m_tipe_eq_mobil-bekas-honda-accord_and_mobil-bekas-honda-br-v
%2Cm_transmission_eq_automatic
%2Cm_year_between_2020_to_2020
%2Cmake_eq_mobil-bekas-honda
&sorting=asc-price'''
filter_brand = f'make_eq_mobil-bekas-{brand.lower()}'
filter_model = f'm_tipe_eq_mobil-bekas-{brand.lower()}-{model.lower()}'
filter_transmission = f'm_transmission_eq_{transmission}'
filter_year = f'm_year_between_{year}_to{year}'
filter_sort = f'&sorting=desc-price'
filtered_url = f'{main_url}?filter={filter_model}%2C{filter_transmission}%2C{filter_year}%2C{filter_brand}'
initial_url = filtered_url+filter_sort
#navigate the browser instance to the input_url DESC first

print(f'Filter : {filter_brand} - {filter_model} - {filter_transmission} - {filter_year} - {filtered_url}')
driver.get(initial_url)

while True:
    '''
    While loop to load all results for the search query by finding and clicking on the "Load More" button unless
    the button doesn't exist i.e., all results loaded, no more results to load. Without this, only the first 20 listings
    will be scraped
    '''
    try:
        print('while Loop')
        # current_url = driver.current_url
        # print(current_url)
        # WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@data-aut-id="btnLoadMore"]')))
        '''Selecting Area'''
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, f"//a[@data-aut-id='location_{area}']")))
        # driver.find_element(By.XPATH, ).click()
        location_found = driver.find_element(By.XPATH, "//a[@data-aut-id='location_Jakarta D.K.I.']")
        
        if location_found.is_displayed() :
            city = location_found.get_attribute('href')
            initial_url = city
            print(city)
            # print(initial_url)
            break
        # '''Selecting Brand'''
        # WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, f'//*[@data-aut-id="location_{brand}"]')))
        # '''Selecting Model'''
        # WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, f'//*[@data-aut-id="location_{model}"]')))
        # '''Selecting Transmission'''
        # WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, f'//*[@data-aut-id="location_{transmission}"]')))
        # '''Selecting Year'''
        # WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, f'//*[@data-aut-id="location_{year}"]')))
        # driver.find_element(By.XPATH, '//*[@data-aut-id="btnLoadMore"]').click()
        # print("Clicked 'Load More'")
    except TimeoutException:
        break

driver.get(initial_url)
'''FIND LISTINGS AND STORE TO A LIST'''
time.sleep(10)
#Finding the UL element containing all the search result items (as list items)
# listings_list = driver.find_element(By.CSS_SELECTOR, "#container > main > div > div > section > div > div > div:nth-child(6) > div._3etsg > div > div:nth-child(2) > ul")
listing_list = driver.find_element(By.XPATH, '//ul[@data-aut-id="itemsList"]')
print('listing found')
#Finding All list items (li) inside the UL list
listings = listing_list.find_elements(By.CSS_SELECTOR, "li")
# listings = listing_list.find_elements(By.XPATH, '//*[@data-aut-id="itemBox"]')
print('listing items found')
print(listings)
#Initialize empty list to store scrapped data (for further writing on a csv file)
scraped_datas = []

# WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//span[@data-aut-id="itemPrice"]')))
#Loop through each list element (list item) and further find required info from their respective XPath
for listing in listings:
    try:
        #Try method 1 for finding elements
        print('starting to itterate high')
        print(listing)
        # highlight = listing.find_element(By.XPATH, "./a/div[1]/div[1]/span")
        # if highlight :
        #     pass
        # WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//span[@data-aut-id="itemPrice"]')))
        price = listing.find_element(By.XPATH, "./a/div[1]/div[2]/span").text
        #odo & year
        # year_and_odo = listing.find_element(By.XPATH, './span[@data-aut-id="itemSubTitle"]').text
        year_and_odo = listing.find_element(By.XPATH, "./a/div[1]/div[2]/div[1]").text
        #if split
        years_n_odo_split = year_and_odo.split(" - ")
        years = years_n_odo_split[0]
        odo = years_n_odo_split[1]
        # short_description = listing.find_element(By.XPATH, '//*[@data-aut-id="itemsList"]').text
        # date_and_loc = listing.find_element(By.XPATH, './*[@data-aut-id="itemDetails"]')
        date_and_loc = listing.find_element(By.XPATH, "./a/div[1]/div[2]/div[3]")
        # date_and_loc_split = date_and_loc.split("<span>")
        date = date_and_loc.text
        loc = date_and_loc.find_element(By.CSS_SELECTOR, 'span').text
        # date_published = listing.find_element(By.XPATH, './*[@data-aut-id="itemsList"]').text
        listing_link = listing.find_element(By.CSS_SELECTOR, "a")
        ad_link = listing_link.get_attribute('href')
        # price = listing.find_element(By.XPATH, "./a/div/span[1]").text
        # year_and_odo = listing.find_element(By.XPATH, "./a/div/span[2]").text
        # short_description = listing.find_element(By.XPATH, "./a/div/span[3]").text
        # location = listing.find_element(By.XPATH, "./a/div/div/span[1]").text
        # date_published = listing.find_element(By.XPATH, "./a/div/div/span[2]").text
        # listing_link = listing.find_element(By.XPATH, "./a")
        # ad_link = listing_link.get_attribute('href')
        #Once data gathered, append them to the scraped_datas list
        # print(price)
        print(price, years, odo, loc, date, ad_link, 'high')
        scraped_datas.append([price, years, odo, loc, date, ad_link, 'high'])
    except NoSuchElementException:
        #If no results being found from method 1, try method 2. If no results found in method 2, pass
        try:
            print('no element high')
            # highlight = listing.find_elements(By.XPATH, "./a/div[1]/div[1]/span")
            # if highlight :
            #     pass
            # price = listing.find_element(By.XPATH, './*[@data-aut-id="itemPrice"]').text
            price = listing.find_element(By.XPATH, "./a/div[1]/div[2]/span").text
            #odo & year
            # year_and_odo = listing.find_element(By.XPATH, './span[@data-aut-id="itemSubTitle"]').text
            year_and_odo = listing.find_element(By.XPATH, "./a/div[1]/div[2]/div[1]").text
            #if split
            years_n_odo_split = year_and_odo.split(" - ")
            years = years_n_odo_split[0]
            odo = years_n_odo_split[1]
            # short_description = listing.find_element(By.XPATH, '//*[@data-aut-id="itemsList"]').text
            # date_and_loc = listing.find_element(By.XPATH, './*[@data-aut-id="itemDetails"]')
            date_and_loc = listing.find_element(By.XPATH, "./a/div[1]/div[2]/div[3]")
            # date_and_loc_split = date_and_loc.split("<span>")
            date = date_and_loc.text
            loc = date_and_loc.find_element(By.CSS_SELECTOR, 'span').text
            # date_published = listing.find_element(By.XPATH, './*[@data-aut-id="itemsList"]').text
            listing_link = listing.find_element(By.CSS_SELECTOR, "a")
            ad_link = listing_link.get_attribute('href')
            # year_and_odo = listing.find_element(By.XPATH, "./a/div/span[2]").text
            # short_description = listing.find_element(By.XPATH, "./a/div/span[3]").text
            # location = listing.find_element(By.XPATH, "./a/div/div/span[1]").text
            # date_published = listing.find_element(By.XPATH, "./a/div/div/span[2]").text
            # listing_link = listing.find_element(By.XPATH, "./a")
            # ad_link = listing_link.get_attribute('href')
            #Once data gathered, append them to the scraped_datas list
            # print(price)
            print(price, years, odo, loc, date, ad_link, 'high')
            scraped_datas.append([price, years, odo, loc, date, ad_link, 'high'])
        except NoSuchElementException:
            pass
        pass

new_url = initial_url.split("&")[0] + "&sorting=asc-price"

driver.get(new_url)
'''FIND LISTINGS AND STORE TO A LIST'''
time.sleep(15)
#Finding the UL element containing all the search result items (as list items)
# listings_list = driver.find_element(By.CSS_SELECTOR, "#container > main > div > div > section > div > div > div:nth-child(6) > div._3etsg > div > div:nth-child(2) > ul")
listing_list = driver.find_element(By.XPATH, '//ul[@data-aut-id="itemsList"]')
print('listing found')
#Finding All list items (li) inside the UL list
listings = listing_list.find_elements(By.CSS_SELECTOR, "li")
# listings = listing_list.find_elements(By.XPATH, '//*[@data-aut-id="itemBox"]')
print('listing items found')
print(listings)

# WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//span[@data-aut-id="itemPrice"]')))
#Loop through each list element (list item) and further find required info from their respective XPath
for listing in listings:
    try:
        #Try method 1 for finding elements
        print('starting to itterate low')
        # highlight = listing.find_elements(By.XPATH, "./a/div[1]/div[1]/span")
        # if highlight :
        #     pass
        # WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//span[@data-aut-id="itemPrice"]')))
        price = listing.find_element(By.XPATH, "./a/div[1]/div[2]/span").text
        #odo & year
        # year_and_odo = listing.find_element(By.XPATH, './span[@data-aut-id="itemSubTitle"]').text
        year_and_odo = listing.find_element(By.XPATH, "./a/div[1]/div[2]/div[1]").text
        #if split
        years_n_odo_split = year_and_odo.split(" - ")
        years = years_n_odo_split[0]
        odo = years_n_odo_split[1]
        # short_description = listing.find_element(By.XPATH, '//*[@data-aut-id="itemsList"]').text
        # date_and_loc = listing.find_element(By.XPATH, './*[@data-aut-id="itemDetails"]')
        date_and_loc = listing.find_element(By.XPATH, "./a/div[1]/div[2]/div[3]")
        # date_and_loc_split = date_and_loc.split("<span>")
        date = date_and_loc.text
        loc = date_and_loc.find_element(By.CSS_SELECTOR, 'span').text
        # date_published = listing.find_element(By.XPATH, './*[@data-aut-id="itemsList"]').text
        listing_link = listing.find_element(By.CSS_SELECTOR, "a")
        ad_link = listing_link.get_attribute('href')
        # price = listing.find_element(By.XPATH, "./a/div/span[1]").text
        # year_and_odo = listing.find_element(By.XPATH, "./a/div/span[2]").text
        # short_description = listing.find_element(By.XPATH, "./a/div/span[3]").text
        # location = listing.find_element(By.XPATH, "./a/div/div/span[1]").text
        # date_published = listing.find_element(By.XPATH, "./a/div/div/span[2]").text
        # listing_link = listing.find_element(By.XPATH, "./a")
        # ad_link = listing_link.get_attribute('href')
        #Once data gathered, append them to the scraped_datas list
        # print(price)
        print(price, years, odo, loc, date, ad_link, 'low')
        scraped_datas.append([price, years, odo, loc, date, ad_link, 'low'])
    except NoSuchElementException:
        #If no results being found from method 1, try method 2. If no results found in method 2, pass
        try:
            print('no element low')
            # highlight = listing.find_elements(By.XPATH, "./a/div[1]/div[1]")
            # if highlight :
            #     pass
            # price = listing.find_element(By.XPATH, './*[@data-aut-id="itemPrice"]').text
            price = listing.find_element(By.XPATH, "./a/div[1]/div[2]/span").text
            #odo & year
            # year_and_odo = listing.find_element(By.XPATH, './span[@data-aut-id="itemSubTitle"]').text
            year_and_odo = listing.find_element(By.XPATH, "./a/div[1]/div[2]/div[1]").text
            #if split
            years_n_odo_split = year_and_odo.split(" - ")
            years = years_n_odo_split[0]
            odo = years_n_odo_split[1]
            # short_description = listing.find_element(By.XPATH, '//*[@data-aut-id="itemsList"]').text
            # date_and_loc = listing.find_element(By.XPATH, './*[@data-aut-id="itemDetails"]')
            date_and_loc = listing.find_element(By.XPATH, "./a/div[1]/div[2]/div[3]")
            # date_and_loc_split = date_and_loc.split("<span>")
            date = date_and_loc.text
            loc = date_and_loc.find_element(By.CSS_SELECTOR, 'span').text
            # date_published = listing.find_element(By.XPATH, './*[@data-aut-id="itemsList"]').text
            listing_link = listing.find_element(By.CSS_SELECTOR, "a")
            ad_link = listing_link.get_attribute('href')
            # year_and_odo = listing.find_element(By.XPATH, "./a/div/span[2]").text
            # short_description = listing.find_element(By.XPATH, "./a/div/span[3]").text
            # location = listing.find_element(By.XPATH, "./a/div/div/span[1]").text
            # date_published = listing.find_element(By.XPATH, "./a/div/div/span[2]").text
            # listing_link = listing.find_element(By.XPATH, "./a")
            # ad_link = listing_link.get_attribute('href')
            #Once data gathered, append them to the scraped_datas list
            # print(price)
            print(price, years, odo, loc, date, ad_link, 'low')
            scraped_datas.append([price, years, odo, loc, date, ad_link, 'low'])
        except NoSuchElementException:
            pass
        pass

'''WRITE SCRAPED LIST TO CSV'''
search_query = f'{random.randint(1,1000)}' #extract the search query form the url
with open(f'scraped_data/{search_query}.csv', 'w', newline='', encoding="utf-8") as file: 
    writer = csv.writer(file)
    headers = ['Price','Year', 'Odo', 'Location', 'Date of Listing', 'Link', "type"]
    writer.writerow(headers)
    for data in scraped_datas:
        writer.writerow(data)
