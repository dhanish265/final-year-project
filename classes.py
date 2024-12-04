import math
from utils import *
from utils import DEPTH, EXTRA_LENGTH

class Anchorage:
    def __init__(self, vertices):
        # Assume valid input of vertices such that origin (0,0) lies inside polygon (completely inside, not on edge, not any of the vertices)
        self.vertices = vertices
        self.edges = create_edges(vertices)
        print(self.edges)
    
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
        

class Vessel:
    def __init__(self, length, arrival, departure, centre = None):
        self.length = length
        self.arrival = arrival
        self.departure = departure
        self.centre = centre
        self.radius = self.length + EXTRA_LENGTH
    
    def checkCollision(self, vessel):
        pass
        
vertices = [(12, -9), (-12, -9), (-12, 20)]
anc = Anchorage(vertices)
vessel = Vessel(1, 1, 1, (-2.5, 7.5))
print(anc.isVesselInside(vessel))
            