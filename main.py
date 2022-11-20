from lib.loader import page_source_loader
from lib.reader import html_scraper
from lib.writer import data_to_csv
from lib.uploader import uploader

print("OLX Web Scraper!")
input_url = input("URL: ")

page_source = page_source_loader(input_url)
data = html_scraper(page_source=page_source)
uploader(data)
data_to_csv(filename='data', data=data)



