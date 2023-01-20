from selenium import webdriver
import time
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests

driver = webdriver.Firefox()

email = "aleksandrdonskov@gmail.com" 
password = "hpkorolev2020"

driver.get("https://korolev.hookah.work/")
email_input = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, 'loginform-email'))
)
password_input = driver.find_element(By.ID, 'loginform-password')
email_input.send_keys(email)
password_input.send_keys(password)

submit = driver.find_element(By.CLASS_NAME, 'btn-primary')
submit.click()

# driver.get("https://korolev.hookah.work/sale/data")

# print(driver.page_source)

time.sleep(1)
cookies = driver.get_cookies()


session = requests.Session()
session.headers.update({'User-Agent': driver.execute_script("return navigator.userAgent;")})
driver.quit()
for cookie in cookies:
    session.cookies.update({cookie['name']: cookie['value']})

import requests
session = requests.Session()

params = {'iDisplayStart': 0, 'iDisplayLength': 6500, 'mDataProp_12': 'created_at', 'bSortable_12': 'true', 'iSortCol_0': 12, 'sSortDir_0': 'desc', 'iSortingCols': 1}
response = session.get("https://korolev.hookah.work/sale/data", params=params)

response = session.get("https://korolev.hookah.work/sale/data?iDisplayStart=0&iDisplayLength=6500&mDataProp_12=created_at&bSortable_12=true&iSortCol_0=12&sSortDir_0=desc&iSortingCols=1")
response = session.get("https://korolev.hookah.work/sale/data?iDisplayStart=0&iDisplayLength=6500&mDataProp_12=created_at&bSortable_12=true&iSortCol_0=12&sSortDir_0=desc&iSortingCols=1")
response = session.get("https://korolev.hookah.work/sale/data?iDisplayStart=0&iDisplayLength=6500&mDataProp_12=created_at&bSortable_12=true&iSortCol_0=12&sSortDir_0=desc&iSortingCols=1")
response = session.get("https://korolev.hookah.work/sale/data?iDisplayStart=0&iDisplayLength=6500&mDataProp_12=created_at&bSortable_12=true&iSortCol_0=12&sSortDir_0=desc&iSortingCols=1")
response = session.get("https://korolev.hookah.work/sale/data?iDisplayStart=0&iDisplayLength=6500&mDataProp_12=created_at&bSortable_12=true&iSortCol_0=12&sSortDir_0=desc&iSortingCols=1")
response = session.get("https://korolev.hookah.work/sale/data?iDisplayStart=0&iDisplayLength=6500&mDataProp_12=created_at&bSortable_12=true&iSortCol_0=12&sSortDir_0=desc&iSortingCols=1")
response = session.get("https://korolev.hookah.work/sale/data?iDisplayStart=0&iDisplayLength=6500&mDataProp_12=created_at&bSortable_12=true&iSortCol_0=12&sSortDir_0=desc&iSortingCols=1")
data = response.json()



sales = data['data']
sales[0]['total']
sales[0]['client_id']





