from lib.loader import page_source_loader
from lib.reader import html_scraper
from lib.uploader import uploader

print("OLX Web Scraper!")
input_url = input("URL: ")

page_source = page_source_loader(input_url)
data = html_scraper(page_source=page_source)

# This uploads the final data to mongodb, You
# may also write the same to a csv file by making use of 
# the data_to_csv function from the lib.writer module.
uploader(data) 



