import argparse

parser = argparse.ArgumentParser()
parser.add_argument("filename", help="name of the file/csv for storing scraped data (extension not required)")
parser.add_argument("-u", "--upload", action="store_true")