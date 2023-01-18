from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from datetime import datetime
import locale
import re

class Sale: 
    title: str
    price: str
    amount: int
    payment_method: str
    client: str
    time_added: datetime

class Scrapper:
    html: list = []
    data: list = []

    def __init__(self, url: str, email: str, password: str):
        self.url = url
        self.email = email
        self.password = password
        self.driver = webdriver.Firefox()

    def scan_first_page(self) -> list:
        self.driver.get(self.url)

        self.html = []

        # Wait for the email input element to be present
        email_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'loginform-email'))
        )
        password_input = self.driver.find_element(By.ID, 'loginform-password')
        email_input.send_keys(self.email)
        password_input.send_keys(self.password)

        submit = self.driver.find_element(By.CLASS_NAME, 'btn-primary')
        submit.click()

        # Wait for the "Продажи" link to be present 
        sales = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.LINK_TEXT, 'Продажи'))
        )
        sales.click()


        # Wait for the page to be fully loaded
        WebDriverWait(self.driver, 10).until(EC.title_is(self.driver.title))
        list = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'select.form-control'))
        )

        list.click()
        option = self.driver.find_element(By.XPATH, ".//option[text()='100']")

        option.click()

        self.html.append(self.driver.page_source)

        self.driver.quit()

        self.clean_data(self.html)

        return self.data

    
    def scan(self) -> list:
        self.driver.get(self.url)

        self.html = []

        # Wait for the email input element to be present
        email_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'loginform-email'))
        )
        password_input = self.driver.find_element(By.ID, 'loginform-password')
        email_input.send_keys(self.email)
        password_input.send_keys(self.password)

        submit = self.driver.find_element(By.CLASS_NAME, 'btn-primary')
        submit.click()

        # Wait for the "Продажи" link to be present 
        sales = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.LINK_TEXT, 'Продажи'))
        )
        sales.click()

        # Wait for the page to be fully loaded
        WebDriverWait(self.driver, 10).until(EC.title_is(self.driver.title))
        list = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'select.form-control'))
        )

        list.click()
        option = self.driver.find_element(By.XPATH, ".//option[text()='100']")

        option.click()

        wait = WebDriverWait(self.driver, 10)
        div = wait.until(EC.visibility_of_element_located((By.ID, "sales_paginate")))
        ul = div.find_element(By.CLASS_NAME,"pagination")
        li = ul.find_element(By.ID, "sales_next")
        a = li.find_element(By.TAG_NAME, "a")
            
        iter = 0

        li = ul.find_element(By.ID, "sales_next")
        while "disabled" not in li.get_attribute("class") and iter < 20:
            iter += 1
            a.click()
            div = wait.until(EC.visibility_of_element_located((By.ID, "sales_paginate")))
            ul = div.find_element(By.CLASS_NAME,"pagination")
            li = ul.find_element(By.ID, "sales_next")
            a = li.find_element(By.TAG_NAME, "a")
            self.html.append(self.driver.page_source)
            

        self.driver.quit()

        self.clean_data(self.html)

        return self.data

    
    def clean_data(self, html: list):

        locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
        for page in html:
            soup = BeautifulSoup(page, 'html.parser')

            rows = soup.find_all('tr', class_=['odd', 'even'])

            for row in rows:
                tds = row.find_all('td')
                sale = Sale()
                sale.title = tds[1].text.strip()
                sale.price = float(tds[4].text.strip())
                sale.amount = int(re.search(r'\d', tds[3].text.strip()).group())
                sale.payment_method = tds[5].text.strip()
                sale.client = tds[9].text.strip()
                sale.time_added = self.convert_to_datetime(tds[12].text.strip())
                self.data.append(sale)
            
    def convert_to_datetime(self, string: str) -> datetime:
        string = self.match_datetime(string)
        datetime_string = datetime.strptime(string, "%d %b. %Y г., %H:%M:%S")
        return datetime_string

    def match_datetime(self, date_string: str) -> str:
        months = {
            "февр.": "фев.",
            "сент.": "сен.",
            "нояб.": "ноя.",
            "мая" : "мая."
        }

        for full, abbreviation in months.items():
            date_string = re.sub(r"(\d{1,2})\s" + full, r"\1 " + abbreviation, date_string)

        return date_string
