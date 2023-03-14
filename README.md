<img align="right" width="150" height="auto" src="https://i.imgur.com/uHdBRp2.png">

# Olx Web Scraper
CLI to Scrape OLX for Ad listing (Optimized for Car/Motocycle ads)

## Table of Contents
  - [Installation](#installation)
  - [Usage](#usage)


## Installation
1. Create a virtual enviroment for the repo & activate it 
```python
python -m venv venv
cd venv
Scripts\activate.bat
```

3. Install the scraper 
```python
pip install olx-web-scraper
```

## Usage
- To get scraping, simple run the following on your prefered terminal:
```python
olx_web_scraper <filename without extension>
```
Eg:
`python
olx_web_scraper scraped_data
`

- Next, input the URL to scrape
```
OLX Web Scraper!
URL: https://www.olx.in/kerala_g2001160/q-interceptor-650
```

- This will then scrape all the listing available and save to a file named scraped_data.csv in your root folder.
<!-- ![](https://i.imgur.com/iptsDh1.png) -->