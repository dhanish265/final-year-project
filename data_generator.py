from numpy import random
from scipy.stats import beta
import xlsxwriter
from openpyxl import load_workbook
import os.path
import bisect
from utils import MIN_IDEAL_DIST, MAX_IDEAL_DIST

LIMIT = 14 * 24 * 60

def generateData(busy_rate = 1, name = 'Synthetic Anchorage (normal)'):
    # workbook = xlsxwriter.Workbook(name  + '.xlsx')
    data = []
    for _ in range(100):
        # worksheet = workbook.add_worksheet(str(i + 1))
        data_sheet = []
        currTime = random.exponential(0.45) * 60
        while currTime < LIMIT:
            data_sheet.append((round(currTime), round(currTime) + round(busy_rate * random.lognormal(2.4, 1.3) * 60), beta.rvs(2.4, 2.4, 30, 270).item()))
            currTime += random.exponential(0.45) * 60
        data.append(data_sheet)
    write_to_xlsx(data, name + '.xlsx', [str(i) for i in range(1, 101)])

    
def read_data(name):
    if not os.path.isfile("data/" + name):
        print("Incorrect file name! Please check!")
        return None
    data = []
    workbook = load_workbook("data/" + name)
    sheetNames = workbook.sheetnames
    for sheetName in sheetNames:
        values = []
        worksheet = workbook[sheetName]
        for row in worksheet.values:
            values.append(row)
        data.append(values)
    return data

# data = read_data('Ahirkapi Anchorage.xlsx')
# if data is not None:
#     print(data[0])
# generateData(busy_rate= 0.5, name = 'Synthetic Anchorage (idle)')

def dwell_time_dist_analysis(rewrite = False):
    value = []
    if not rewrite:
        data = read_data('dwell_time_analysis.xlsx')[0]
        for row in data:
            value.append(row[-1])
        return value
    
    data = [[] for i in range(730)]
    for _ in range(100):
        data2 = []
        for j in range(730):
            data2.append(round(random.lognormal(2.4, 1.3) * 60))
        data2.sort()
        for j in range(730):
            # print(j)
            data[j].append(data2[j])
    for j in range(730):
        average = sum(data[j])/len(data[j])
        data[j].append(average)
        value.append(average)
    write_to_xlsx([data], 'dwell_time_analysis.xlsx', ['normal']) 
    return value

def write_to_xlsx(data, book_name: str, sheet_names: list[str]):
    workbook = xlsxwriter.Workbook(book_name)
    for i, data_sheet in enumerate(data):
        worksheet = workbook.add_worksheet(sheet_names[i])
        row = 0
        while row < len(data_sheet):
            col = 0
            while col < len(data_sheet[row]):
                worksheet.write(row, col, data_sheet[row][col])
                col += 1
            row += 1
    workbook.close()

times = dwell_time_dist_analysis(rewrite = False)
boundaries = [(times[i] + times[i+1])/2 for i in range(len(times) - 1)]
# print(boundaries)
# print(times)
# the times are obtained as [a, b, c, d, ... y, z]
# using this, if the dwell time of a vessel is between 0 and (a+b)/2, it's ideal anchoring distance from entry side is 445
# likewise, if it is > (y+z)/2, it's ideal anchoring distance is 2500 - 445 = 2055
# everything in between is evenly distributed between 445 and 2055 (i.e., if dwell time is in between (a+b)/2 and (b+c)/2, 445 + (2025-445)/(26-1))

def obtain_ideal_distance(dwell_time):
    print(MIN_IDEAL_DIST + bisect.bisect(boundaries, dwell_time) * (MAX_IDEAL_DIST - MIN_IDEAL_DIST)/(len(boundaries)))
    pass

obtain_ideal_distance(19.52)



