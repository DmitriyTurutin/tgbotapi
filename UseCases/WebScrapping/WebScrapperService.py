from datetime import datetime
from Infrastructure.ScrapperService import Scrapper
from Infrastructure.GenerateExcel import GenerateExcel
from Infrastructure.Persistence.Repository import Repository
from Infrastructure.GenerateBarPlot import GenerateBarPlot
from Entities.Sale import Sale
from Infrastructure.model import Model
import concurrent.futures


class WebScrapperService:
    repository = Repository()

    generateExcel = GenerateExcel()
    plotGenerator = GenerateBarPlot()

    def set_email_url(self, email, url):
        self.model = Model(email, url)

    def login(self, address: str, email: str, password: str) -> None:
        scrapper_service = Scrapper(address, email, password)
        sales: list[Sale] = scrapper_service.scan_first_page()

        if sales:
            self.repository.add_sales_data(email, address, sales)
        else:
            print("No Sales Found!!")


    def scan(self, url: str, email: str, password: str):
        scrapper_service = Scrapper(url, email, password)
        sales: list[Sale] = scrapper_service.scan()

        if sales is not None:
            self.repository.add_sales_data(email, url, sales)
            self.model.generate_model()
        else:
            print("Sales is none!!")

    def get_from_to(self, from_date: datetime, to_date: datetime, email, url):
        data = self.repository.get_time_period(from_date, to_date, email, url)
        data = list(map(lambda element: element[1:], data))
        self.generateExcel.generate_excel(data, email)
        self.plotGenerator.generate_bar_plot(data, email)
        return data

    def get_today(self, email, url):
        data = self.repository.get_today(email, url)
        data = list(map(lambda element: element[1:], data))
        self.generateExcel.generate_excel(data, email)
        self.plotGenerator.generate_bar_plot(data, email)
        return data

    def get_last_month(self, email, url):
        data = self.repository.get_last_month(email, url)
        data = list(map(lambda element: element[1:], data))
        self.generateExcel.generate_excel(data, email)
        self.plotGenerator.generate_bar_plot(data, email)
        return data
