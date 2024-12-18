import copy
import math

import numpy as np
from utils import *
from utils import DEPTH, EXTRA_LENGTH

class Anchorage:
    def __init__(self, vertices):
        # Assume valid input of vertices such that origin (0,0) lies inside polygon (completely inside, not on edge, not any of the vertices)
        self.vertices = vertices
        self.edges = create_edges(vertices)
        self.anchored = []
        print(self.edges)
    
    def isVesselInside(self, vessel):
        x, y = vessel.centre
        return checkVesselInside(self.edges, x, y, vessel.radius)
    
    def generateCornerPoints(self, vessel):
        # generate side-and-side
        cornerPoints = []
        for i in range(len(self.edges)):
            edge = self.edges[i]
            for j in range(i+1, len(self.edges)):
                edge2 = self.edges[j]
                if edge[0] == edge2[0] == 0:
                    continue
                if edge[1] == edge2[1] == 0:
                    continue
                if edge2[1] * edge[0] == edge[1] * edge2[0]:
                    continue
                A = [[edge[0], edge[1]], [edge2[0], edge2[1]]]
                Y = [edge[-1], edge2[-1]]
                value1 = math.sqrt(edge[0] * edge[0] + edge[1] * edge[1])
                value2 = math.sqrt(edge2[0] * edge2[0] + edge2[1] * edge2[1])
                Y[0] -= abs(vessel.radius * value1)
                Y[1] -= abs(vessel.radius * value2)
                print(A, Y)
                res = tuple(np.linalg.inv(A).dot(Y))
                res = (res[0].item(), res[1].item())
                # check if generated corner point collides with existing anchored point:
                collision = False
                for vessel2 in self.anchored:
                    x, y = vessel2.centre
                    # print(x, y)
                    if checkCircleCollision(res[0], x, res[1], y, vessel.radius, vessel2.radius):
                        collision = True
                        break
                if not collision:
                    cornerPoints.append(res)
        return cornerPoints
        

class Vessel:
    def __init__(self, length, centre = None, arrival = 0, departure = 60):
        self.length = length
        self.arrival = arrival
        self.departure = departure
        self.centre = centre
        self.radius = self.length + EXTRA_LENGTH
    
    def collidesWith(self, vessel): # tangent circles are not considered colliding.
        x1, y1 = self.centre
        x2, y2 = vessel.centre
        r1, r2 = self.radius, vessel.radius
        return checkCircleCollision(x1, x2, y1, y2, r1, r2)

        
vertices = [(12, -9), (-12, -9), (-12, 20)]
anc = Anchorage(vertices)
vessel = Vessel(2)
vessel2 = Vessel(3, (-8.5, 11))
anc.anchored.append(vessel2)
cp = anc.generateCornerPoints(vessel)
print(cp)
# print(anc.isVesselInside(vessel))
# print(vessel.collidesWith(vessel2))
            