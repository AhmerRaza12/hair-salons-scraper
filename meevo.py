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
import datetime

load_dotenv()

options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36')
options.add_argument('--start-maximized')

chrome_install = ChromeDriverManager().install()

folder = os.path.dirname(chrome_install)
chromedriver_path = os.path.join(folder, "chromedriver.exe")

service = ChromeService(chromedriver_path)
driver = webdriver.Chrome(service=service, options=options)

email = os.getenv("JCP_MEEVO_EMAIL")
password = os.getenv("JCP_MEEVO_PASSWORD")
print(email)
print(password)

store_names_extracted = []
def login():
   
    time.sleep(4)
    user_name = driver.find_element(By.XPATH, "//input[@aria-label='OB.USER_NAME']")
    for char in email:
        user_name.send_keys(char)
    time.sleep(1)
    password_textbox = driver.find_element(By.XPATH, "//input[@aria-label='OB.PASSWORD']")
    for char in password:
        password_textbox.send_keys(char)
    time.sleep(1)
    login_button = driver.find_element(By.XPATH, "//button[.='Log in']")
    time.sleep(1)
    login_button.click()
    time.sleep(5)
    try:
        service_booking = driver.find_element(By.XPATH, "//button[contains(.,'Book a Service')]")
        service_booking.click()
        time.sleep(10)
    except:
        pass
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


def get_location_add_columns(ids):
    id= ids[0]
    print(id)
    driver.get(f'https://jcp.meevo.com/CustomerPortal/onlinebooking/booking/guestinfo?tenantId=1&locationId={id}')
    time.sleep(8)
    if '/login' in driver.current_url:
        login()
    next_button = driver.find_element(By.XPATH, "//button[contains(.,'Next')]")
    next_button.click()
    time.sleep(1)
    textured_styling = driver.find_element(By.XPATH, "//div[.='Textured Styling']")
    textured_styling.click()
    time.sleep(1)
    micro_braids = driver.find_element(By.XPATH,"//div[contains(@class, 'service-header') and contains(text(), 'MICRO BRAIDS')]/ancestor::div[@class='flex-row flex']/input[@type='radio']")
    if micro_braids.is_selected() == False and micro_braids:
        micro_braids.click()
        time.sleep(3)
        next_button = driver.find_element(By.XPATH, "//button[contains(.,'Next')]")
        next_button.click()
        time.sleep(1)
        driver.wait_for_request('https://jcp.meevo.com/onlinebooking/api/ob/scanforopenings')
        requests = driver.requests
        unique_dates = set()
        unique_employees = set()
        employee_prices = set()
        unique_days = set()
        for request in requests:
            if request.response:
                if 'https://jcp.meevo.com/onlinebooking/api/ob/scanforopenings' in request.url:
                    encoding = request.response.headers.get('Content-Encoding', '')
                    response_body = request.response.body
                
                    if encoding == 'br':
                        response_body = brotli.decompress(response_body).decode('utf-8')
                    else:
                        response_body = response_body.decode('utf-8')
                
                    data_list = json.loads(response_body)
                        
                    for data in data_list:
                        service_openings = data.get('serviceOpenings', [])
                        for opening in service_openings:
                            unique_dates.add(opening.get('date'))
                            unique_employees.add(opening.get('employeeDisplayName'))
                            employee_prices.add(str(opening.get('employeePrice')))
        driver.requests.clear()
        number_of_people = len(unique_employees)
        for date in unique_dates:
            date = date.split('T')[0]
            date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
            day = date.strftime('%A')
            unique_days.add(day)
        days_offered_micro_braids = list(unique_days)
        people_offering_micro_braids = list(unique_employees)
        price_ranges_micro_braids = list(employee_prices)
        price_ranges_micro_braids.sort()

        data={
            'Number of People Offering Micro Braids': number_of_people,
            'Days Offered Micro Braids': ', '.join(days_offered_micro_braids),
            'People Offering Micro Braids': ', '.join(people_offering_micro_braids),
            'Price Ranges Micro Braids': ', '.join(price_ranges_micro_braids)
        }
        print(data)
    else:
        data={
            'Number of People Offering Micro Braids': '',
            'Days Offered Micro Braids': '',
            'People Offering Micro Braids': '',
            'Price Ranges Micro Braids': ''
        }
        print('No Micro Braids')


ids=[]
df=pd.read_excel('meevo_salons.xlsx')
for i in df['Id']:
    ids.append(i)

get_location_add_columns(ids)
# login()

# all_data = get_data()




