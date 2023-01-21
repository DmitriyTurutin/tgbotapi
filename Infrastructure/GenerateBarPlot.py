import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from collections import Counter
import numpy as np


class GenerateBarPlot:
    def generate_bar_plot(self, sales_data, i):
        # Extract the hour from each timestamp and count the number of sales for each hour
        hour_counts = Counter(sale[5].hour for sale in sales_data)
        # Get the hours and counts from the Counter object
        hours = np.array(list(hour_counts.keys()))
        counts = np.array(list(hour_counts.values()))

        # Set the x-axis labels to the hours
        plt.xticks(hours)
        plt.title("График распределения продаж по часам")

        plt.gca().xaxis.set_major_formatter(FuncFormatter(lambda x, _: int(x)))

        # Generate the barplot
        plt.bar(hours, counts)

        plt.xlabel("Время")
        plt.ylabel("Кол-во заказов")

        # Save the plot to an image file
        plt.savefig(f'./Storage/sales_{i}.png')
