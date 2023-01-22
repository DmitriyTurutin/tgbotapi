from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import requests
import concurrent.futures
from datetime import datetime
from Entities.Sale import Sale
import requests
import time
import locale
import re


class Scrapper:
    data: list[Sale]

    def __init__(self, url: str, email: str, password: str):
        self.url = url
        self.email = email
        self.password = password
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')

        self.driver = webdriver.Chrome(chrome_options=options)


    def scan_first_page(self) -> list:
        self.driver.get("https://korolev.hookah.work/")
        email_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'loginform-email'))
        )
        password_input = self.driver.find_element(By.ID, 'loginform-password')
        email_input.send_keys(self.email)
        password_input.send_keys(self.password)

        submit = self.driver.find_element(By.CLASS_NAME, 'btn-primary')
        submit.click()
        
        wait = WebDriverWait(self.driver, 10)
        wait.until(EC.presence_of_element_located((By.ID, "table-booking-container")))


        cookies = self.driver.get_cookies()

        session = requests.Session()
        session.headers.update({'User-Agent': self.driver.execute_script("return navigator.userAgent;")})
        self.driver.quit()
        for cookie in cookies:
            session.cookies.update({cookie['name']: cookie['value']})

        list_of_data = []

        params = {'iDisplayStart': 0, 'iDisplayLength': 100, 'mDataProp_12': 'created_at', 'bSortable_12': 'true',
                  'iSortCol_0': 12, 'sSortDir_0': 'desc', 'iSortingCols': 1}
        response = session.get("https://korolev.hookah.work/sale/data", params=params)
        list_of_data.append(response.json()['data'])
        return_data = self.clean_data_new(list_of_data)
        return return_data

    def scan(self) -> list:
        self.driver.get("https://korolev.hookah.work/")
        email_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'loginform-email'))
        )
        password_input = self.driver.find_element(By.ID, 'loginform-password')
        email_input.send_keys(self.email)
        password_input.send_keys(self.password)

        submit = self.driver.find_element(By.CLASS_NAME, 'btn-primary')
        submit.click()

        time.sleep(1)
        cookies = self.driver.get_cookies()

        session = requests.Session()
        session.headers.update({'User-Agent': self.driver.execute_script("return navigator.userAgent;")})
        self.driver.quit()
        for cookie in cookies:
            session.cookies.update({cookie['name']: cookie['value']})

        number_of_database_elements = session.get("https://korolev.hookah.work/sale/data")
        number_of_database_elements = int(number_of_database_elements.json()['iTotalRecords'])
        iterations = number_of_database_elements // 6500
        i = 0

        list_of_data = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = [executor.submit(self.get_data, i, session) for i in range(iterations)]

            for future in concurrent.futures.as_completed(results):
                list_of_data.append(future.result())

        last_item = number_of_database_elements - 6500 * iterations
        params = {'iDisplayStart': i * 6500, 'iDisplayLength': last_item, 'mDataProp_12': 'created_at',
                'bSortable_12': 'true', 'iSortCol_0': 12, 'sSortDir_0': 'desc', 'iSortingCols': 1}
        response = session.get("https://korolev.hookah.work/sale/data", params=params)
        list_of_data.append(response.json()['data'])

        return_data = self.clean_data_new(list_of_data)

        return return_data

    
    def get_data(self, i: int, session: requests.Session) -> dict:
        params = {'iDisplayStart': i * 6500 - 6500, 'iDisplayLength': 6500, 'mDataProp_12': 'created_at',
                'bSortable_12': 'true', 'iSortCol_0': 12, 'sSortDir_0': 'desc', 'iSortingCols': 1}
        response = session.get("https://korolev.hookah.work/sale/data", params=params)
        return response.json()['data']

    def clean_data_new(self, list_of_data: list):
        locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
        data: list[Sale] = []
        for data_item in list_of_data:
            for sale_item in data_item:
                sale = Sale()
                sale.title = sale_item['product_id']
                sale.price = float(sale_item['total'])
                sale.amount = 1
                sale.payment_method = sale_item['payment_method_id'].strip()
                sale.client = sale_item['client_id'].strip()
                sale.time_added = self.convert_to_datetime(sale_item['created_at'].strip())
                data.append(sale)
        return data

    def convert_to_datetime(self, string: str) -> datetime:
        string = self.match_datetime(string)
        datetime_string = datetime.strptime(string, "%d %b. %Y г., %H:%M:%S")
        return datetime_string

    def match_datetime(self, date_string: str) -> str:
        months = {
            "февр.": "фев.",
            "сент.": "сен.",
            "нояб.": "ноя.",
            "мая": "мая."
        }

        for full, abbreviation in months.items():
            date_string = re.sub(r"(\d{1,2})\s" + full, r"\1 " + abbreviation, date_string)

        return date_string
