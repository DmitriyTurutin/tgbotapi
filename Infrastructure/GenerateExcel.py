import pandas as pd

class GenerateExcel: 
    def generate_excel(self, data, email):
        df = pd.DataFrame(data, columns=['title', 'price', 'amount', 'payment_method', 'client', 'time_added'])
        df['time_added'] = df['time_added'].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S'))


        df.to_excel(f"Storage/sales_{email}.xlsx", index=False)