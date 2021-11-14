from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup
import csv

url = "https://www.olx.in/kerala_g2001160/cars_c84/q-polo-gt"

service = Service('./chromedriver.exe')
driver = webdriver.Chrome(service=service)
driver.get(url)

while True:
    try:
        time.sleep(10)
        driver.find_element(By.XPATH, value='//*[@data-aut-id="btnLoadMore"]').click()
        print("Clicked 'Load more'")
    except NoSuchElementException:
        break

content = driver.page_source
soup = BeautifulSoup(content, "html.parser")

listings = soup.find_all("li", class_="_31j8e")

datas = []
for listing in listings:
    price = listing.find("span", class_="_3GOwr").text
    detail = listing.find("div", class_="KFHpP").text
    desc = listing.find("div", class_="_4aNdc")
    description = descgi.get('title')
    location = listing.find("div", class_="_1zvfB").text
    date_of_list = location.find("span")
    link = listing.find('a', href=True)
    ad_link = link.get('href')
    datas.append([price, detail, description, location, date_of_list, ad_link])

with open('scraped_data.csv', 'w', newline='', encoding="utf-8") as file:
    writer = csv.writer(file)
    headers = ['Price','Detail','Description', 'Location', 'Date of Listing', 'Link']
    writer.writerow(headers)
    for data in datas:
        writer.writerow(data)
