from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

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
driver=webdriver.Chrome(service=service, options=options)

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

# def get_data():
#     driver.wait_for_request('https://jcp.meevo.com/onlinebooking/api/ob/LocationAccess/List')
#     requests = driver.requests
#     for request in requests:
#         if request.response:
#             if 'https://jcp.meevo.com/onlinebooking/api/ob/LocationAccess/List' in request.url:
#                 encoding = request.response.headers.get('Content-Encoding', '')
#                 response_body = request.response.body
            
#                 if encoding == 'br':
#                     response_body = brotli.decompress(response_body).decode('utf-8')
#                 else:
#                     response_body = response_body.decode('utf-8')
            
#                 data = json.loads(response_body)
           
#                 data = [location for location in data if 'Salon' in location['storeName']]
#                 for i, location in enumerate(data):
                    
#                     id = location['locationId'] if 'locationId' in location else ''
#                     store_name = location['storeName'] if 'storeName' in location else ''
#                     address = location['address1'] if 'address1' in location else ''
#                     city = location['city'] if 'city' in location else ''
#                     state= location['state'] if 'state' in location else ''
#                     zip_code = location['zipCode'] if 'zipCode' in location else ''
#                     phone_number = location['phoneNumber'] if 'phoneNumber' in location else ''
#                     data={
#                         'Id': id,
#                         'Store Name': store_name,
#                         'Address': address,
#                         'City': city,
#                         'State': state,
#                         'Zip Code': zip_code,
#                         'Phone Number': phone_number
#                     }
#                     all_data.append(data)
#     return all_data

all_data=[]
def get_micro_braids_data(ids):
    for id in ids:
        driver.get(f'https://jcp.meevo.com/CustomerPortal/onlinebooking/booking/guestinfo?tenantId=1&locationId={1013}')
        time.sleep(15)
        if '/login' in driver.current_url:
            login()
        time.sleep(3)
        next_button = driver.find_element(By.XPATH, "//button[contains(.,'Next')]")
        next_button.click()
        time.sleep(1)
        textured_styling = driver.find_element(By.XPATH, "//div[.='Textured Styling']")
        textured_styling.click()
        time.sleep(1)
        try:
            micro_braids = driver.find_element(By.XPATH,"//div[contains(@class, 'service-header') and contains(text(), 'MICRO BRAIDS')]/ancestor::div[@class='flex-row flex']/input[@type='radio']")
            micro_braids.click()
            time.sleep(3)
            next_button = driver.find_element(By.XPATH, "//button[contains(.,'Next')]")
            next_button.click()
            time.sleep(5)
            people = driver.find_elements(By.XPATH, "//div[span[text()='with']]")
            openings= driver.find_elements(By.XPATH, "//header[h4[@class='text-2xl font-semibold text-green-600 ng-star-inserted']]")
            prices= driver.find_elements(By.XPATH,"//ob-booking-opening//div[@class='text-black font-bold ng-star-inserted']")
            if openings:
                prices_list=[]
                for price in prices:
                    if price.text not in prices_list:
                        prices_list.append(price.text)
                prices_list.sort()
                days=[]
                for opening in openings:
                    day = opening.text.split(',')[0]
                    if day not in days:
                        days.append(day)
                people_names = []
                for person in people:
                    full_text = person.text
                    if full_text.startswith('with '):
                        print(full_text)
                        name = full_text[5:].strip()
                        if name and name not in people_names:
                            people_names.append(name)
                number_of_people = len(people_names)
                data={
                    "Number Of People Offering Micro Braids": number_of_people,
                    "Days Offering Micro Braids": ", ".join(days),
                    "Price Range":", ".join(prices_list),
                    "People Offering Micro Braids": ", ".join(people_names)
                }
                print(data)
                # add the data to the excel file with the id matching the column and write these columns to the respective rows
                df=pd.read_excel('meevo_salons.xlsx')
                df.loc[df['Id']==id,'Number Of People Offering Micro Braids']=number_of_people
                df.loc[df['Id']==id,'Days Offering Micro Braids']=", ".join(days)
                df.loc[df['Id']==id,'Price Range']=", ".join(prices_list)
                df.loc[df['Id']==id,'People Offering Micro Braids']=", ".join(people_names)
                df.to_excel('meevo_salons.xlsx',index=False)
            else:
                data={
                    "Number Of People Offering Micro Braids": '',
                    "Days Offering Micro Braids": '',
                    "Price Range": '',
                    "People Offering Micro Braids": ''     
                }
                print(data)
                df=pd.read_excel('meevo_salons.xlsx')
                df.loc[df['Id']==id,'Number Of People Offering Micro Braids']=''
                df.loc[df['Id']==id,'Days Offering Micro Braids']=''
                df.loc[df['Id']==id,'Price Range']=''
                df.loc[df['Id']==id,'People Offering Micro Braids']=''
                df.to_excel('meevo_salons.xlsx',index=False)
        
        except:
            data={
                "Number Of People Offering Micro Braids": '',
                "Days Offering Micro Braids": '',
                "Price Range": '',
                "People Offering Micro Braids": ''     
            }
            print(data)
            df=pd.read_excel('meevo_salons.xlsx')
            df.loc[df['Id']==id,'Number Of People Offering Micro Braids']=''
            df.loc[df['Id']==id,'Days Offering Micro Braids']=''
            df.loc[df['Id']==id,'Price Range']=''
            df.loc[df['Id']==id,'People Offering Micro Braids']=''
            df.to_excel('meevo_salons.xlsx',index=False)






ids=[]
df=pd.read_excel('meevo_salons.xlsx')
for i in df['Id']:
    ids.append(i)

get_micro_braids_data(ids)

# login()

# all_data = get_data()




