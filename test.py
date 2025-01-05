import polylabel_code
import numpy as np

polygon = np.array([(12, -9), (-12, -9), (-12, 20), (12, -9)])
hole = np.array([(-12, 7), (-12, 3), (-8, 3), (-8, 7), (-12, 7)])
hole2 = np.array([(2.5, -9), (8.5, -9), (8.5, -3), (2.5, -3), (2.5, -9)])
# ring1 = np.array([[1, 2], [3, 4], [5, 1], [3, 2], [1, 2]])
# ring2 = np.array([[2.5, 3], [3, 3], [3, 2.5], [2.5, 3]])
# ring3 = np.array([[2, 2.25], [2.5, 2.25], [2.5, 2.75], [2, 2.5]])
rings = [polygon, hole, hole2]
cell = polylabel_code.polylabel(rings, precision=0.01)
print(cell.c, cell.d)
# polylabel_code.polylabel([polygon, hole], precision=10**-6)