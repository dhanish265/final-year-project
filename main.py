from classes import *
from utils import *
import data_generator
from data_generator import dwell_times, boundaries, dwell_time_raw_data

data_generator.instantiate_times()
# print(times[0])
# data_generator.obtain_ideal_distance(243.22)

queue, time_list = [], []
anchorage_name = 'Synthetic Anchorage (normal)'
#synthetic: [(2000, 1250), (2000, -1250), (-2000, -1250), (-2000, 1250)]
busy_rate = 1
anchorage = Anchorage([(2000, 1250), (2000, -1250), (-2000, -1250), (-2000, 1250)])

raw_data = data_generator.read_data(anchorage_name)
sample = raw_data['1']

for i, row in enumerate(sample):
    arrival, departure, radius = row
    time_list.append((arrival, 1, i+1, radius))
    time_list.append((departure, -1, i+1, radius))
time_list.sort()
# print(time_list)


