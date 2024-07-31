from seleniumwire import webdriver  
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
from dotenv import load_dotenv
import json
import brotli
import pandas as pd
import csv

load_dotenv()

options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3')
options.add_argument('--start-maximized')

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

email = os.getenv("JCP_MEEVO_EMAIL")
password = os.getenv("JCP_MEEVO_PASSWORD")
print(email)
print(password)

store_names_extracted = []
def login():
    driver.get('https://jcp.meevo.com/CustomerPortal/login?tenantId=1')
    time.sleep(4)
    user_name = driver.find_element(By.XPATH, "//input[@aria-label='OB.USER_NAME']")
    for char in email:
        user_name.send_keys(char)
        time.sleep(0.1)
    time.sleep(1)
    password_textbox = driver.find_element(By.XPATH, "//input[@aria-label='OB.PASSWORD']")
    for char in password:
        password_textbox.send_keys(char)
        time.sleep(0.1)
    time.sleep(1)
    login_button = driver.find_element(By.XPATH, "//button[.='Log in']")
    time.sleep(1)
    login_button.click()
    time.sleep(5)
    service_booking = driver.find_element(By.XPATH, "//button[contains(.,'Book a Service')]")
    service_booking.click()
    time.sleep(10)
    # store_names = driver.find_elements(By.XPATH, "//div[@class='m-b-5 location-name']")
    # for store_name in store_names:
    #     store_names_extracted.append(store_name.text)
    # return store_names_extracted




all_data=[]

def get_data():
    driver.wait_for_request('https://jcp.meevo.com/onlinebooking/api/ob/LocationAccess/List')
    requests = driver.requests
    for request in requests:
        if request.response:
            if 'https://jcp.meevo.com/onlinebooking/api/ob/LocationAccess/List' in request.url:
                encoding = request.response.headers.get('Content-Encoding', '')
                response_body = request.response.body
            
                if encoding == 'br':
                    response_body = brotli.decompress(response_body).decode('utf-8')
                else:
                    response_body = response_body.decode('utf-8')
            
                data = json.loads(response_body)
           
                data = [location for location in data if 'Salon' in location['storeName']]
                for i, location in enumerate(data):
                    
                    id = location['locationId'] if 'locationId' in location else ''
                    store_name = location['storeName'] if 'storeName' in location else ''
                    address = location['address1'] if 'address1' in location else ''
                    city = location['city'] if 'city' in location else ''
                    state= location['state'] if 'state' in location else ''
                    zip_code = location['zipCode'] if 'zipCode' in location else ''
                    phone_number = location['phoneNumber'] if 'phoneNumber' in location else ''
                    data={
                        'Id': id,
                        'Store Name': store_name,
                        'Address': address,
                        'City': city,
                        'State': state,
                        'Zip Code': zip_code,
                        'Phone Number': phone_number
                    }
                    all_data.append(data)
    return all_data


login()

# all_data = get_data()




