from numpy import random
from scipy.stats import beta
import xlsxwriter
from openpyxl import load_workbook
import os.path

LIMIT = 14 * 24 * 60
# print(LIMIT)
def generateData(busy_rate = 1, name = 'Synthetic Anchorage (normal)'):
    workbook = xlsxwriter.Workbook(name  + '.xlsx')
    for i in range(100):
        worksheet = workbook.add_worksheet(str(i + 1))
        data = []
        currTime = random.exponential(0.45) * 60
        while currTime < LIMIT:
            data.append((round(currTime), round(currTime) + round(busy_rate * random.lognormal(2.4, 1.3) * 60), beta.rvs(2.4, 2.4, 30, 270).item()))
            currTime += random.exponential(0.45) * 60
        row = 0
        for arrival, departure, length in data:
            worksheet.write(row, 0, arrival)
            worksheet.write(row, 1, departure)
            worksheet.write(row, 2, length)
            row += 1
    workbook.close()
    # print(data)
    # print(len(data))
    
def read_data(name):
    if not os.path.isfile("data/" + name):
        print("Incorrect file name! Please check!")
        return None
    data = []
    workbook = load_workbook("data/" + name)
    for i in range(100):
        values = []
        worksheet = workbook[str(i + 1)]
        for row in worksheet.values:
            values.append(row)
        data.append(values)
    return data

# data = read_data('Synthetic Anchorage (normal).xlsx')
# if data is not None:
#     print(data[1])
# generateData(busy_rate= 0.5, name = 'Synthetic Anchorage (idle)')

data2 = []
for i in range(100):
    data2.append(round(random.lognormal(2.4, 1.3) * 60))
print(max(data2))
# data2.sort()
# print(data2[75])
# print(sum(data2)/len(data2))

