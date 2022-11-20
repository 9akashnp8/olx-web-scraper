from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def page_source_loader(input_url):
    service = Service(executable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
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
        except ( NoSuchElementException, TimeoutException, StaleElementReferenceException ):
            break

    return driver.page_source