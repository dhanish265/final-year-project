import main
from classes import *
from utils import *
from data_generator import read_data, write_to_xlsx
import time as tm
import json

# anchorage_name = 'Ahirkapi Anchorage'
anchorage_name = 'test_0.45'
# anchorage_name = 'Synthetic Anchorage (normal)'
raw_data = read_data(anchorage_name)
data = []
method = 'SPSA'

samples = []
samples.append([(60, 600, 856), (120, 800, 456), (180, 700, 606), (240, 750, 306), (450, 900, 606)])
samples.append([(60, 480, 856), (490, 800, 456), (520, 700, 606), (600, 750, 306)])

def process_steady(totals):
    data = []
    for total in totals:
        entry = []
        entry.append(total['time'])
        entry.append(0) if total['d'][1] == 0 else entry.append(total['d'][0]/total['d'][1])
        aid = 0 if total['ra'][1] == 0 else total['ra'][0]/total['ra'][1]
        did = 0 if total['rd'][1] == 0 else total['rd'][0]/total['rd'][1]
        entry.append((aid + did)/2)
        entry.append(0) if total['t'][1] == 0 else entry.append(total['t'][0]/total['t'][1])
        entry.append(total['area'])
        entry.append(total['util'])
        data.append(entry)
    return data

def process_time(times):
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
    start_time = tm.ctime(tm.time())
    totals, nodeAssignment, plannerAssignment = anc_planner.run_main()
    end_time = tm.ctime(tm.time())

    # print(totals, nodeAssignment, plannerAssignment, sep='\n\n')
    
    # print(factors)
    for total in totals:
        print(total)
    data = process_steady(totals)
    for x in nodeAssignment:
        if x not in plannerAssignment:
            print('mismatch')
        if nodeAssignment[x] is None and plannerAssignment[x] is not None:
            print('mismatch')
        if nodeAssignment[x] is not None and (plannerAssignment[x] is None or plannerAssignment[x] != nodeAssignment[x]):
            print('mismatch')
    # data.append((risk, util, dist, time))
    # data = process(factors)
    # data.append(factors['time'])
    # data2 = process_util(totals['u'])
    # print(data)
    # print(data2)
    print(start_time, end_time)
    print(len([x for x in nodeAssignment if nodeAssignment[x] is None]))
    write_to_xlsx([data], 'test_main' + '2.xlsx', sheet_names=['data'])
    
    
    f = open('file.json', 'w')
    json.dump(totals, f, indent = 2)
    