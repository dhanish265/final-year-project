import main
from classes import *
from utils import *
from data_generator import read_data, write_to_xlsx

# anchorage_name = 'Ahirkapi Anchorage'
anchorage_name = 'test_0.90_2'
raw_data = read_data(anchorage_name)
data = []

samples = []
samples.append([(60, 600, 856), (120, 800, 456), (180, 700, 606), (240, 750, 306), (450, 900, 606)])
samples.append([(60, 480, 856), (490, 800, 456), (520, 700, 606), (600, 750, 306)])

def process(factors):
    data = {'r': [0], 'd': [0], 't': [0]}
    vesselNum = 1
    totalR, totalD, totalT = 0, 0, 0
    while vesselNum < len(factors['r']):
        totalR += factors['r'][vesselNum]
        totalD += factors['d'][vesselNum]
        totalT += factors['t'][vesselNum]
        data['r'].append(totalR/vesselNum)
        data['d'].append(totalD/vesselNum)
        data['t'].append(totalT/vesselNum)
        vesselNum += 1
        
    return [data['r'], data['d'], data['t']]

def process_util(times):
    data2 = [[], []]
    for time, area in times:
        data2[0].append(area.item())
        data2[1].append(time)
    return data2

for i in range(1, 2):
# for sample in samples:
    sample = raw_data[str(i)]
    # print(i)
    anc_planner = main.AnchoragePlanner(standard=False)
    area = areaMaxInscribedCircle(anc_planner.anchorage)
    anc_planner.populate_time_list(sample)
    factors = {'r': [0], 'd': [0], 't': [0], 'time': [0]}
    totals, nodeAssignment, plannerAssignment = anc_planner.run_alternate(method='NDE', factors = factors)
    # print(totals, nodeAssignment, plannerAssignment, sep='\n\n')
    # print(factors)
    util = obtainAverageEffectiveRemainingArea(totals['u'], area)
    risk = totals['r']/len(anc_planner.vessels)
    dist = totals['d']/len(anc_planner.vessels)
    time = totals['t']/len(anc_planner.vessels)
    # data.append((risk, util, dist, time))
    data = process(factors)
    data.append(factors['time'])
    data2 = process_util(totals['u'])
    print(data)
    print(data2)
    write_to_xlsx([data, data2], 'test_warm_up_NDE_0.90_2.xlsx', sheet_names=['data', 'util'])
    