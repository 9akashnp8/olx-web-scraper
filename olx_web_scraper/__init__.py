from .utils.loader import page_source_loader
from .utils.reader import html_scraper
from .utils.uploader import uploader
from .utils.writer import data_to_csv
from .utils.parser import parser

def main():
    args = parser.parse_args()

    print("OLX Web Scraper!")
    input_url = input("URL: ")

    page_source = page_source_loader(input_url)
    data = html_scraper(page_source=page_source)

    # This uploads the final data to mongodb, You
    # may also write the same to a csv file by providing
    # the -u or --upload flag
    if args.upload:
        uploader(data)
    else:
        data_to_csv(filename=args.filename, data=data)



