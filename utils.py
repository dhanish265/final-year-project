from copy import deepcopy
import math
import polylabel_code
import numpy as np
from polylabel_code import polylabel

DEPTH = 35
EXTRA_LENGTH = math.sqrt((25*math.sqrt(DEPTH)) ** 2 - DEPTH**2)
# EXTRA_LENGTH = 0
EPSILON = 10 ** (-6)
MIN_IDEAL_DIST = 445
MAX_IDEAL_DIST = 2055 #2500 - 445
MAX_WIDTH = 2500
SPSA_WEIGHTS = [np.array([0.053, 0.325, 0.117, -0.287, 0.087, -0.121, -0.219]), np.array([0.019, 0.525, 0.150, -0.729, -0.559, 0.733, -0.389]), np.array([-0.100, 0.614, -0.020, -0.134, -0.406, -0.274, -0.304]), np.array([-0.066, 0.580, -0.002, -0.372, 0.240, 0.712, -0.882]), np.array([-0.185, 0.155, -0.393, 0.189, -0.219, -0.291, -0.559])]
BEAM_LENGTH = 5
EXPANSION_SIZE = 5

def calculateArea(vertices):
    vertices.append(vertices[0])
    area = 0
    for i in range(len(vertices) - 1):
        area += (vertices[i][0] * vertices[i+1][1] - vertices[i][1] * vertices[i+1][0])
        # print(area)
    del vertices[-1]
    return abs(area)/2
    

def create_edges(vertices):
    # each edge is encoded as [a, b, c]
    # ax + by <= c
    edges = []
    vertices.append(vertices[0])
    for i in range(1, len(vertices)):
        x1, y1 = vertices[i]
        x2, y2 = vertices[i-1]
        if x1 == x2: # vertical line
            edges.append([x1//abs(x1), 0, abs(x1)])
            continue
        if y1 == y2: # horizontal line
            edges.append([0, y1//abs(y1), abs(y1)])
            continue
        a = y1-y2
        b = x2-x1
        c = b*y1 + a*x1
        if c > 0:
            edges.append([a, b, c])
        else: edges.append([-a, -b, -c])
    del vertices[-1]
    return edges
    
def checkVesselInside(edges, x, y, radius):
    for edge in edges:
        a, b, c = edge
        # check if centre of circle is inside boundary
        if a*x + b*y >= c:
            return False
        # check if circle intersects edge twice
        # if perp. dist between edge and circle is smaller than radius, means the edge is too close to the centre of the circle
        diff = abs(a*x + b*y - c) ** 2 - (a**2 + b**2) * (radius**2)
        if diff < -EPSILON:
            return False
    return True

def checkCircleCollision(x1, x2, y1, y2, r1, r2):
    # print(x1, x2, y1, y2, r1, r2)
    # print(x1, y1, x2, y2)
    dist = ((x1-x2) ** 2 + (y1-y2)**2)
    inter = dist - (r1 + r2) ** 2
    if inter >= -EPSILON:
        return False
    else: return True
    
def findIntersectionsLineCircle(x, y, r, a, b, c):
    if abs(b) < EPSILON:
        x1 = c/a
        inter = r*r - (x1-x)**2
        if abs(inter) < EPSILON:
            return [(x1, y)]
        elif inter < 0:
            return []
        y1 = math.sqrt(inter) + y
        y2 = -math.sqrt(inter) + y
        return [(x1, y1), (x1, y2)]
    
    L = 1 + a*a/(b*b)
    M = 2* (a/b*(y-c/b) -x)
    N = c*c/(b*b) + x*x + y*y - r*r - 2*c*y/b
    disc = M*M - 4*N*L
    # print(x, y, r, a, b, c)
    # print(L, M, N, disc)
    if abs(disc) < EPSILON:
        x1 = -M/2
        y1 = (c-a*x1)/b
        return [(x1, y1)]
    elif disc < 0:
        return []
    x1 = (-M + math.sqrt(disc))/(2 * L)
    x2 = (-M - math.sqrt(disc))/(2 * L)
    y1 = (c-a*x1)/b
    y2 = (c-a*x2)/b
    return [(x1, y1), (x2, y2)]

def areaMaxInscribedCircle(anchorage):
    vertices = deepcopy(anchorage.vertices)
    vertices.append(vertices[0])
    polygon = np.array(vertices)
    rings = [polygon]
    
    for vessel in anchorage.anchored:
        vertices = vessel.obtainCircumscribingHexagon()
        vertices.append(vertices[0])
        rings.append(np.array(vertices))
        
    # print(rings)
    
    cell = polylabel(rings, precision=10)
    r = cell.d
    # print(cell.c, r)
    return math.pi * r * r

    
    
def calculateScore(metrics, numVessels):
    return np.dot(metrics, np.array([0.1, 0.1, 0.1, 0.1, 0.5, 0.1]))/numVessels

def obtainAverageEffectiveRemainingArea(t, totalArea):
    total = t[0][0] * totalArea
    totalTime = t[-1][0]
    for i in range(len(t) - 1):
        total += (t[i+1][0] - t[i][0]) * t[i][1]
    return total/(totalTime * totalArea)
    
def calculateNDE(x, y, anc):
    NDE = MAX_WIDTH
    for edge in anc.edges:
        a, b, c = edge
        if b == 0:
            continue
        y2 = (c - a * x)/b
        if y2 <= y:
            continue
        inside = True
        for a2, b2, c2 in anc.edges:
            if a2 * x + b2 * y2 > c2:
                inside = False
                break
        if not inside:
            continue
        NDE = min(y2 - y, NDE)
    return NDE

def calculateIntersectionDistance(vessel, anchoredVessels, x, y, calculateDID = True):
    AID, EDID = 0, 0
    for ancVessel in anchoredVessels:
        intersection = findIntersectionsLineCircle(ancVessel.centre[0], ancVessel.centre[1], ancVessel.radius, 1, 0, x)
        if len(intersection) < 2 or y > max(intersection[1][1], intersection[0][1]):
            continue
        AID += abs(intersection[1][1] - intersection[0][1])
        if not calculateDID:
            continue
        if vessel.departure >= ancVessel.departure:
            EDID += abs(intersection[1][1] - intersection[0][1])
    return AID, EDID




# def round_to_1(x):
#     return round(x, -int(math.floor(math.log10(abs(x)))))

# print(round_to_1(5.5))
# x = 1
# y = 3
# r = 2
# # a = -1
# # b = -math.sqrt(3)
# # c = 4 - 3*math.sqrt(3) 
# # print(c)
# a = 1
# b = 0
# c = 2
# print(findIntersectionsLineCircle(x, y, r, a, b, c))
# print(EPSILON)
    