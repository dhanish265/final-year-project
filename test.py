# import polylabel_code
# import numpy as np
# import classes
# import main

# # polygon = np.array([(12, -9), (-12, -9), (-12, 20), (12, -9)])
# # hole = np.array([(-12, 7), (-12, 3), (-8, 3), (-8, 7), (-12, 7)])
# # hole2 = np.array([(2.5, -9), (8.5, -9), (8.5, -3), (2.5, -3), (2.5, -9)])
# # ring1 = np.array([[1, 2], [3, 4], [5, 1], [3, 2], [1, 2]])
# # ring2 = np.array([[2.5, 3], [3, 3], [3, 2.5], [2.5, 3]])
# # ring3 = np.array([[2, 2.25], [2.5, 2.25], [2.5, 2.75], [2, 2.5]])

# # polygon = np.array([(2000, 1250), (2000, -1250), (-2000, -1250), (-2000, 1250), (2000, 1250)])
# # rings = [polygon]

# # vessel = classes.Vessel(856, centre=(1000, -250))
# # vertices = vessel.obtainCircumscribingHexagon()
# # vertices.append(vertices[0])
# # rings.append(np.array(vertices))

# # cell = polylabel_code.polylabel(rings, precision=0.5)
# # print(cell.c, cell.d)
# # polylabel_code.polylabel([polygon, hole], precision=10**-6)

# # class Object:
# #     def __init__(self):
# #         self.arr = []

# # class Test:
# #     def __init__(self):
# #         self.arr = [] 
        
# # obj1 = Object()
# # obj2 = Object()
# # obj1.arr.append(1)
# # obj1.arr.append(2)
# # test = Test()
# # test.arr.append(obj1)

# # arr = test.arr[0].arr
# # arr.pop(0)
# # print(test.arr[0].arr)

# ancPlanner = main.AnchoragePlanner()

# y = main.QueueNode(ancPlanner.anchorage)
# y.waiting = [1]
# ancPlanner.queue.append((1, y))
# ancPlanner.queue.append((0, main.QueueNode(ancPlanner.anchorage)))
# print(ancPlanner.queue[1][1].waiting)
# ancPlanner.queue.sort(key = lambda x: x[0])

# print(ancPlanner.queue[1][1].waiting)

# from utils import calculateScore

# met = np.array([0.1, 0.1, 0.1, 0.1, 0.5, 0.1])
# print(calculateScore(met, 2))