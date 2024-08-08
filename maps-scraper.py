from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
from selenium import webdriver
import requests
import os
import pandas
from bs4 import BeautifulSoup
import re
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.common.exceptions import TimeoutException
from datetime import datetime
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import WebDriverException
import pandas as pd
import csv
from dotenv import load_dotenv
from urllib.parse import urlparse, parse_qs


Options = webdriver.ChromeOptions()
Options.add_argument('--no-sandbox')
Options.add_argument('--disable-dev-shm-usage')
Options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3')
Options.add_argument('--start-maximized')

chrome_install = ChromeDriverManager().install()
folder = os.path.dirname(chrome_install)
chromedriver_path = os.path.join(folder, "chromedriver.exe")

service = ChromeService(chromedriver_path)
driver=webdriver.Chrome(service=service, options=Options)

def appendProduct(file_path2, data):
    temp_file = 'temp_file.csv'
    if os.path.isfile(file_path2):
        df = pd.read_csv(file_path2, encoding='utf-8')
    else:
        df = pd.DataFrame()

    df_new_row = pd.DataFrame([data])
    df = pd.concat([df, df_new_row], ignore_index=True)

    try:
        df.to_csv(temp_file, index=False, encoding='utf-8')
    except Exception as e:
        print(f"An error occurred while saving the temporary file: {str(e)}")
        return False

    try:
        os.replace(temp_file, file_path2)
    except Exception as e:
        print(f"An error occurred while replacing the original file: {str(e)}")
        return False

    return True

def scroll_and_click(driver, scrollable_div):
    prev_height = driver.execute_script("return arguments[0].scrollHeight", scrollable_div)
    
    while True:
        driver.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight)", scrollable_div)
        time.sleep(3)
        
        try:
            end_indicator = driver.find_element(By.CSS_SELECTOR, "span[class$='HlvSq']")
            print("Reached the end of the scrollable content.")
            return True
        except:
            pass
        
        new_height = driver.execute_script("return arguments[0].scrollHeight", scrollable_div)
        if new_height == prev_height:
            stores = driver.find_elements(By.CSS_SELECTOR, "div.Nv2PK.THOPZb.CpccDe")
            if stores:
                driver.execute_script("arguments[0].scrollIntoView();", stores[-1])
                stores[-1].click()
                time.sleep(7)
            else:
                print("No more stores to click, assuming end of content.")
                return False
        prev_height = new_height

def get_all_stores():
    scrollable_div = driver.find_element(By.XPATH, "//*[@id='QA0Szd']/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]")
    while True:
        if scroll_and_click(driver, scrollable_div):
            break

def scrape_data(city):
    driver.get(f"https://www.google.com/maps/search/hair+braid+{city}/4z/data=!4m2!2m1!6e1?entry=ttu")
    time.sleep(5)
    get_all_stores()
    time.sleep(5)
    stores=driver.find_elements(By.CSS_SELECTOR, "div.Nv2PK.THOPZb.CpccDe")
    for store in stores:
        driver.execute_script("arguments[0].scrollIntoView();", store)
        store.click()
        time.sleep(4)
        try:
            store_name=driver.find_element(By.XPATH, "//h1[@class='DUwDvf lfPIob']").text
        except:
            store_name=""
        try:
            rating=driver.find_element(By.XPATH, "//div[@class='F7nice ']//span//span[@aria-hidden='true']").text
        except:
            rating=""
        try:
            no_of_reviews=driver.find_element(By.XPATH, "//div[@class='F7nice ']/span[2]").text
            no_of_reviews= str.replace(no_of_reviews, "(", "")
            no_of_reviews= str.replace(no_of_reviews, ")", "")

        except:
            no_of_reviews=""
        try:
            address=driver.find_element(By.XPATH, "//button[@data-item-id='address']//div[@class='Io6YTe fontBodyMedium kR99db ']").text
        except:
            address=""
        try:
            website=driver.find_element(By.XPATH, "//a[@data-item-id='authority']").get_attribute("href")
            parsed_url = urlparse(website)
            actual_url = parse_qs(parsed_url.query).get('q', [None])[0]
        except:
            actual_url=""
        try:
            phone_number=driver.find_element(By.XPATH, "//button[@data-tooltip='Copy phone number']//div[@class='Io6YTe fontBodyMedium kR99db ']").text
        except:
            phone_number=""
        
        data={
            "Store Name": store_name,
            "Address": address,
            "Rating": rating,
            "No of Reviews": no_of_reviews,
            "Website": actual_url,
            "Phone Number": phone_number
        }
        appendProduct("uk_stores.csv", data)

cities =  [
     "solihull", "basingstoke", "chelmsford"
]


for city in cities:
    scrape_data(city)

driver.quit()