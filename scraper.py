#Import required selenium modules
from pickle import FALSE
import re
import psycopg2
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
        self.service = Service(executable_path=ChromeDriverManager().install())
        #create a chrome webdriver instance
        self.driver = webdriver.Chrome(service=self.service)
        self.db_init()
    
    def db_init(self):
        self.connection = psycopg2.connect(user="postgres",
                                  password="Broom2021",
                                  host="price-scraping.cessoy2t6pfz.ap-southeast-3.rds.amazonaws.com",
                                  port="5432",
                                  database="postgres")
        self.cursor = self.connection.cursor()

    def db_check(self):
        args_str = ''
        for x in self.scraped_datas:
            args_str = f"{args_str},'{x[6]}'"
        print(args_str)
        postgres_search_query = f"SELECT url FROM car_lists WHERE url IN ({args_str[1:]})"
        print(postgres_search_query)
        self.cursor.execute(postgres_search_query)
        result = [r[0] for r in self.cursor.fetchall()]
        print(result)


    def db_insert(self):
        args_str = ''
        for x in self.scraped_datas:
            prices = re.sub("[^0-9]", "", x[1]) 
            args_str = f"{args_str},('{x[0]}',{prices},'{x[2]}','{x[3]}','{x[4]}','{x[5]}','{x[6]}','{x[7]}')"
        print(args_str)
        # postgres_search_query = "SELECT url FROM car_lists WHERE url IN " + args_str
        postgres_insert_query = "INSERT INTO car_lists (car_type, price, years, odo, created_at, loc, url, price_type) VALUES " + args_str[1:]
        # record_to_insert = (5, 'One Plus 6', 950)
        print(postgres_insert_query)
        self.cursor.execute(postgres_insert_query)

        self.connection.commit()
        count = self.cursor.rowcount
        print(count, "Record inserted successfully into db")

    def main_setup(self):
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

        #Set data according to list
        self.area = list(filter(lambda a: self.input_area.capitalize() in a, self.area_list))[0]
        # print("area is :" + area[0])
        self.brand = list(filter(lambda b: self.input_brand.capitalize() in b, self.brand_list))[0]
        self.model = self.input_model
        self.transmission = 'manual' if self.input_transmission.lower() == 'manual' else 'automatic'
        self.year = self.input_year

        print(f'INPUT : {self.area} - {self.brand} - {self.model} - {self.transmission} - {self.year}')

        '''https://www.olx.co.id/jakarta-selatan_g4000030/mobil-bekas_c198
        ?filter=m_tipe_eq_mobil-bekas-honda-accord_and_mobil-bekas-honda-br-v
        %2Cm_transmission_eq_automatic
        %2Cm_year_between_2020_to_2020
        %2Cmake_eq_mobil-bekas-honda
        &sorting=asc-price'''
        filter_brand = f'make_eq_mobil-bekas-{self.brand.lower()}'
        filter_model = f'm_tipe_eq_mobil-bekas-{self.brand.lower()}-{self.model.lower()}'
        filter_transmission = f'm_transmission_eq_{self.transmission}'
        filter_year = f'm_year_between_{self.year}_to_{self.year}'
        filter_sort = f'&sorting=desc-price'
        filtered_url = f'{self.main_url}?filter={filter_model}%2C{filter_transmission}%2C{filter_year}%2C{filter_brand}'
        self.initial_url = filtered_url+filter_sort
        #navigate the browser instance to the input_url DESC first
        print(f'Filter : {filter_brand} - {filter_model} - {filter_transmission} - {filter_year} - {filtered_url}')
        self.driver.get(self.initial_url)
    
    def switch_area(self):
        time.sleep(10)
        location_found = self.driver.find_element(By.XPATH, f"//a[@data-aut-id='location_{self.area}']")
        city = location_found.get_attribute('href')
        self.initial_url = city
        print(city)
        # while True:
        #     '''
        #     While loop to load all results for the search query by finding and clicking on the "Load More" button unless
        #     the button doesn't exist i.e., all results loaded, no more results to load. Without this, only the first 20 listings
        #     will be scraped
        #     '''
        #     try:
        #         print('while Loop')
        #         # current_url = driver.current_url
        #         # print(current_url)
        #         # WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@data-aut-id="btnLoadMore"]')))
        #         '''Selecting Area'''
        #         # WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, f"//a[@data-aut-id='location_{self.area}']")))
        #         # driver.find_element(By.XPATH, ).click()
        #         location_found = self.driver.find_element(By.XPATH, f"//a[@data-aut-id='location_{self.area}']")
        #         city = location_found.get_attribute('href')
        #         self.initial_url = city
        #         print(city)
                
        #         # if location_found.is_displayed() :
        #             # print(initial_url)
        #         # '''Selecting Brand'''
        #         # WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, f'//*[@data-aut-id="location_{brand}"]')))
        #         # '''Selecting Model'''
        #         # WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, f'//*[@data-aut-id="location_{model}"]')))
        #         # '''Selecting Transmission'''
        #         # WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, f'//*[@data-aut-id="location_{transmission}"]')))
        #         # '''Selecting Year'''
        #         # WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, f'//*[@data-aut-id="location_{year}"]')))
        #         # driver.find_element(By.XPATH, '//*[@data-aut-id="btnLoadMore"]').click()
        #         # print("Clicked 'Load More'")
        #     except TimeoutException:
        #         break
    
    def list_extraction(self):
        self.driver.get(self.initial_url)
        '''FIND LISTINGS AND STORE TO A LIST'''
        time.sleep(10)
        #Finding the UL element containing all the search result items (as list items)
        # listings_list = driver.find_element(By.CSS_SELECTOR, "#container > main > div > div > section > div > div > div:nth-child(6) > div._3etsg > div > div:nth-child(2) > ul")
        listing_list = self.driver.find_element(By.XPATH, '//ul[@data-aut-id="itemsList"]')
        print('listing found')
        #Finding All list items (li) inside the UL list
        listings = listing_list.find_elements(By.CSS_SELECTOR, "li")
        # listings = listing_list.find_elements(By.XPATH, '//*[@data-aut-id="itemBox"]')
        print('listing items found')
        print(listings)
        return listings
        #Initialize empty list to store scrapped data (for further writing on a csv file)

        # WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//span[@data-aut-id="itemPrice"]')))
        #Loop through each list element (list item) and further find required info from their respective XPath
    
    def data_extraction(self, listings, price_type):
        for listing in listings:
            try:
                #Try method 1 for finding elements
                print('starting to itterate ' + price_type )
                print(listing)

                listing.find_element(By.XPATH, "./a/div[1]/div[1]/span").text
                # WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//span[@data-aut-id="itemPrice"]')))
            except NoSuchElementException:

                #If no results being found from method 1, try method 2. If no results found in method 2, pass
                try:
                    
                    price = listing.find_element(By.XPATH, "./a/div[1]/div[2]/span").text
                    #odo & year
                    # year_and_odo = listing.find_element(By.XPATH, './span[@data-aut-id="itemSubTitle"]').text
                    year_and_odo = listing.find_element(By.XPATH, "./a/div[1]/div[2]/div[1]").text
                    short_desc = listing.find_element(By.XPATH, "./a/div[1]/div[2]/div[2]")
                    car_type = short_desc.get_attribute('title')
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
                    # print(car_type, price, years, odo, loc, date, ad_link, price_type)
                    exist_in = any(ad_link in x for x in self.scraped_datas)
                    print(exist_in)
                    if exist_in != True:
                        self.scraped_datas.append([car_type, price, years, odo, loc, date, ad_link, price_type])
                except NoSuchElementException:
                    pass
                pass
        if price_type == 'high':
            self.initial_url = self.initial_url.split("&")[0] + "&sorting=asc-price"
        else:
            pass
    
    def write_to_csv(self):
        '''WRITE SCRAPED LIST TO CSV'''
        search_query = f'{random.randint(1,1000)}' #extract the search query form the url
        with open(f'scraped_data/{search_query}.csv', 'w', newline='', encoding="utf-8") as file: 
            writer = csv.writer(file)
            headers = ['Price','Year', 'Odo', 'Location', 'Date of Listing', 'Link', "type"]
            writer.writerow(headers)
            for data in self.scraped_datas:
                writer.writerow(data)

    def check_highlight(self):
        try:
            self.driver.find_elements(By.CSS_SELECTOR,'//td[@class="capabilities"]/span')
        except NoSuchElementException:
            print("There are no child 'span' elements")

execute_scrap = Scraper()
execute_scrap.main_setup()
execute_scrap.switch_area()
high_list = execute_scrap.list_extraction()
execute_scrap.data_extraction(high_list, 'high')
low_list = execute_scrap.list_extraction()
execute_scrap.data_extraction(low_list, 'low')
time.sleep(10)
execute_scrap.db_check()
execute_scrap.db_insert()