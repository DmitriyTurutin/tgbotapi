from datetime import datetime
from Infrastructure.Persistence.SalesRepository import SalesRepository
from Infrastructure.ScrapperService import Scrapper
from Infrastructure.GenerateExcel import GenerateExcel
from Infrastructure.GenerateBarPlot import GenerateBarPlot
from Entities.Sale import Sale
# from Infrastructure.model import Model
import concurrent.futures



class WebScrapperService:
    salesRepository = SalesRepository()
    plotGenerator = GenerateBarPlot()
    generateExcel = GenerateExcel()
    # model = Model()

    def login(self, address: str, email: str, password: str) -> None:
        scrapper_service = Scrapper(address, email, password)
        sales: list[Sale] = scrapper_service.scan_first_page()

        if sales is not None:
            for sale in sales:
                self.salesRepository.add(sale)
        else:
            print("Sales is none!!")

    def scan(self, url: str, email: str, password: str):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            scrapper_future = executor.submit(Scrapper(url, email, password).scan)
            sales = scrapper_future.result()
            if sales:
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    self.salesRepository.add(sales)
                    # self.model.generate_model()
            else:
                print("Sales is none!!")

    # def scan(self, url: str, email: str, password: str):
    #     scrapper_service = Scrapper(url, email, password)
    #     sales: list[Sale] = scrapper_service.scan()
    #     print(sales[0])
    #     if sales is not None:
    #         for sale in sales:
    #             self.salesRepository.add(sale)
    #         self.model.generate_model()
    #     else:
    #         print("Sales is none!!")

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
