import math
from utils import *
from utils import DEPTH, EXTRA_LENGTH

class Anchorage:
    def __init__(self, vertices):
        # Assume valid input of vertices such that origin (0,0) lies inside polygon (completely inside, not on edge, not any of the vertices)
        self.vertices = vertices
        self.edges = create_edges(vertices)
        self.anchored = []
        # print(self.edges)
    
    def isVesselInside(self, vessel):
        x, y = vessel.centre
        for edge in self.edges:
            a, b, c = edge
            # check if centre of circle is inside boundary
            if a*x + b*y >= c:
                return False
            # check if circle intersects edge twice
            # if perp. dist between edge and circle is smaller than radius, means the edge is too close to the centre of the circle
            dist = abs(a*x + b*y - c)/math.sqrt(a**2 + b**2)
            # print(dist)
            if dist < vessel.radius:
                return False
        return True
    
    def generateCornerPoints(self, vessel):
        pass
        

class Vessel:
    def __init__(self, length, arrival, departure, centre = None):
        self.length = length
        self.arrival = arrival
        self.departure = departure
        self.centre = centre
        self.radius = self.length + EXTRA_LENGTH
    
    def collidesWith(self, vessel): # tangent circles are not considered colliding.
        x1, y1 = self.centre
        x2, y2 = vessel.centre
        r1, r2 = self.radius, vessel.radius
        dist = math.sqrt((x1-x2) ** 2 + (y1-y2)**2)
        # print(dist, r1+r2)
        if dist >= r1 + r2:
            return False
        else: return True

        
vertices = [(12, -9), (-12, -9), (-12, 20)]
anc = Anchorage(vertices)
vessel = Vessel(2, 1, 1, (-2.5, 7.5))
vessel2 = Vessel(0.5, 1, 1, (1.5, 7))
# print(anc.isVesselInside(vessel))
# print(vessel.collidesWith(vessel2))
            