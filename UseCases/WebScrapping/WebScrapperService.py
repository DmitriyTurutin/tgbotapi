from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import locale
import re
from datetime import datetime
from Infrastructure.Persistence.SalesRepository import SalesRepository
import time
from Infrastructure.GenerateExcel import GenerateExcel
from Infrastructure.GenerateBarPlot import GenerateBarPlot
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class WebScrapperService:
    salesRepository = SalesRepository()
    plotGenerator = GenerateBarPlot() 
    generateExcel = GenerateExcel()

    def login(self, address: str, email: str, password: str) -> None:
        driver = webdriver.Firefox()
        driver.get(address)

        # Wait for the email input element to be present
        email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'loginform-email'))
        )
        password_input = driver.find_element(By.ID, 'loginform-password')
        email_input.send_keys(email)
        password_input.send_keys(password)

        submit = driver.find_element(By.CLASS_NAME, 'btn-primary')
        submit.click()

        # Wait for the "Продажи" link to be present 
        sales = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.LINK_TEXT, 'Продажи'))
        )
        sales.click()

        # Wait for the page to be fully loaded
        WebDriverWait(driver, 10).until(EC.title_is(driver.title))

        html = driver.page_source
        driver.close()

        self.save_data(html)

    def get_from_to(self, from_date: datetime, to_date: datetime):
        data = self.salesRepository.get_time_period(from_date, to_date)
        self.generateExcel.generate_excel(data)
        self.plotGenerator.generate_bar_plot(data)
        return data

    def get_today(self):
        data = self.salesRepository.get_today()
        self.generateExcel.generate_excel(data)
        self.plotGenerator.generate_bar_plot(data) 
        return data

    def get_last_month(self):
        data = self.salesRepository.get_last_month()
        self.generateExcel.generate_excel(data)
        self.plotGenerator.generate_bar_plot(data)
        return data

    def save_data(self, html: str):
        soup = BeautifulSoup(html, 'html.parser')
        locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')

        rows = soup.find_all('tr', class_=['odd', 'even'])

        for row in rows:
            tds = row.find_all('td')
            title = tds[1].text.strip()
            price = float(tds[4].text.strip())
            amount = int(re.search(r'\d', tds[3].text.strip()).group())
            payment_method = tds[5].text.strip()
            time_added_unformatted = tds[12].text.strip()
            time_added = datetime.strptime(
                time_added_unformatted, "%d %b. %Y г., %H:%M:%S")
            self.salesRepository.add(
                title, price, amount, payment_method, "client", time_added)
