import pandas as pd
from Infrastructure.Persistence.SalesRepository import SalesRepository

class GenerateExcel:
    repository = SalesRepository()

    def generate_for_one_month(self):
        data = self.repository.get_last_month()

        df = pd.DataFrame(data, columns=['title', 'price', 'amount', 'payment_method', 'client', 'time_added'])
        df['time_added'] = df['time_added'].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S'))


        df.to_excel("Storage/sales.xlsx", index=False)
    
    def generate_excel(self, data):
        df = pd.DataFrame(data, columns=['title', 'price', 'amount', 'payment_method', 'client', 'time_added'])
        df['time_added'] = df['time_added'].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S'))


        df.to_excel("Storage/sales.xlsx", index=False)