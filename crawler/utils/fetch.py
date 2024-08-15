import csv
import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def fetch_webpage(url: str) -> str:
    """
    Fetches the content of a webpage.

    Args:
        url (str): The URL of the webpage to fetch.

    Returns:
        str: The HTML content of the webpage if the request is successful, None otherwise.
    """

    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})

    # Set up the Chrome WebDriver to run in headless mode (in docker container)
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920x1080")

    # Use the ChromeDriverManager to automatically download the correct version of the ChromeDriver
    service = Service('/usr/bin/chromedriver')
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get(url)
    
    # Will concat all the pages
    html = driver.page_source

    button = driver.find_element(By.ID, 'ASPx_船舶即時動態_DXPagerBottom_PBN')
    i = 0
    while True:
        if i%20 == 19:
            button.click()
            time.sleep(5)

            html += driver.page_source

            button = driver.find_element(By.ID, 'ASPx_船舶即時動態_DXPagerBottom_PBN')

            if button.get_attribute('onclick') == None:
                break

        i = i+1

    driver.close()
    if response.status_code == 200:
        return html
    else:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
        return None

def fetch_ship_berth_order(url: str) -> list[dict]:
    """
    Fetches data from the Kaohsiung Port website using Selenium.

    Args:
        url (str): The URL of the webpage to fetch data from.

    Returns:
        list[dict]: A list of dictionaries containing the scraped data.
    """
    # Set up the Chrome WebDriver to run in headless mode (in docker container)
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920x1080")

    # Use the ChromeDriverManager to automatically download the correct version of the ChromeDriver
    service = Service('/usr/bin/chromedriver')
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        # Navigate to the website
        driver.get(url)

        # Wait for the table to load
        table = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "dxgvControl_PlasticBlue"))
        )

        # Create a list to store table data
        data = []

        # Extract table headers
        headers = [th.text.strip() for th in table.find_elements(By.CLASS_NAME, "dxgvHeader_PlasticBlue")]

        # Extract data from table rows
        rows = table.find_elements(By.CSS_SELECTOR, ".dxgvDataRow_PlasticBlue, .dxgvDataRow_PlasticBlue.dxgvDataRowAlt_PlasticBlue")
        for row in rows:
            # Extract data from each cell
            row_data = [td.text.strip() for td in row.find_elements(By.CLASS_NAME, "dxgv")]
            data.append(dict(zip(headers, row_data)))

        return data

    except Exception as e:
        print(f"Error: {str(e)}")
        return []

    finally:
        # Close the browser
        driver.quit()