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
        self.area = calculateArea(vertices)
        # print(self.area)
        # print(self.edges)
    
    def isVesselInside(self, vessel):
        if vessel.centre is None:
            return None
        x, y = vessel.centre
        return checkVesselInside(self.edges, x, y, vessel.radius)
    
    def calculateHoleDegree(self, cornerPoint, radius):
        distances = []
        x, y = cornerPoint
        for vessel in self.anchored:
            distances.append(math.sqrt((vessel.centre[1] - y) ** 2 + (vessel.centre[0] - x) ** 2) - vessel.radius - radius)
        for a, b, c in self.edges:
            distances.append(abs(a*x + b*y - c)/math.sqrt(a**2 + b**2) - radius)
        distances.sort()
        return 1 - distances[2]/radius #first 2 are bound to be zero due to cornerpoint being tangent to at least two surfaces 
    
    def generateCornerPoints(self, vessel): #vessel is vessel to be placed
        radius = vessel.radius
        cornerPoints = []
        for i in range(len(self.edges)):
            edge = self.edges[i]
            self.generateSideandSideCP(radius, cornerPoints, i, edge)
            self.generateSideandCircleCP(radius, cornerPoints, edge)
        self.generateCircleandCircleCP(radius, cornerPoints)
        return cornerPoints

    def generateCircleandCircleCP(self, radius, cornerPoints):
        for i in range(len(self.anchored)):
            vessel2 = self.anchored[i]
            for j in range(i+1, len(self.anchored)):
                vessel3 = self.anchored[j]
                x2, y2 = vessel2.centre
                x3, y3 = vessel3.centre
                r2, r3 = vessel2.radius + radius, vessel3.radius + radius
                a, b = 2*(x3-x2), 2 *(y3-y2)
                c = r2**2 - r3**2 - x2**2 + x3**2 - y2**2 + y3**2
                res = findIntersectionsLineCircle(x2, y2, r2, a, b, c)
                # print(res)
                self.checkAndAddCP(cornerPoints, res, radius)

    def generateSideandCircleCP(self, radius, cornerPoints, edge):
        a, b = edge[0], edge[1]
        for j in range(len(self.anchored)):
            vessel2 = self.anchored[j]
            # print(vessel2.centre, vessel2.radius)
            c = edge[-1] - (math.sqrt(edge[0] * edge[0] + edge[1] * edge[1]) * radius)
            x, y = vessel2.centre
            r = vessel2.radius + radius
            # print(x, y, r, a, b, c)
            res = findIntersectionsLineCircle(x, y, r, a, b, c)
            # print(res)
            self.checkAndAddCP(cornerPoints, res, radius)

    def checkAndAddCP(self, cornerPoints, res, radius):
        for x1, y1, in res:
            satisfied = True
            if not checkVesselInside(self.edges, x1, y1, radius):
                satisfied = False
            if not satisfied:
                continue
            for ship in self.anchored:
                x2, y2 = ship.centre
                if checkCircleCollision(x1, x2, y1, y2, radius, ship.radius):
                    satisfied = False
                    break
            if satisfied:
                cornerPoints.append((x1, y1))

    def generateSideandSideCP(self, radius, cornerPoints, i, edge):
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
            Y[0] -= abs(radius * value1)
            Y[1] -= abs(radius * value2)
            # print(A, Y)
            res = tuple(np.linalg.inv(A).dot(Y))
            res = (res[0].item(), res[1].item())
                # check if generated corner point collides with existing anchored point:
            collision = False
            for vessel2 in self.anchored:
                x, y = vessel2.centre
                    # print(x, y)
                if checkCircleCollision(res[0], x, res[1], y, radius, vessel2.radius):
                    collision = True
                    break
            if not collision:
                cornerPoints.append(res)
        

class Vessel:
    def __init__(self, length, centre = None, arrival = 0, departure = 60, number = 0):
        self.length = length
        self.arrival = arrival
        self.departure = departure
        self.centre = centre
        self.radius = self.length + EXTRA_LENGTH
        self.number = number
    
    def collidesWith(self, vessel): # tangent circles are not considered colliding.
        if self.centre is None or vessel.centre is None:
            return None
        x1, y1 = self.centre
        x2, y2 = vessel.centre
        r1, r2 = self.radius, vessel.radius
        return checkCircleCollision(x1, x2, y1, y2, r1, r2)
    
    def obtainCircumscribingHexagon(self):
        x, y = self.centre
        r = self.radius
        vertices = []
        vertices.append((x-2*r/math.sqrt(3), y))
        vertices.append((x-r/math.sqrt(3), y+r))
        vertices.append((x+r/math.sqrt(3), y+r))
        vertices.append((x+2*r/math.sqrt(3), y))
        vertices.append((x+r/math.sqrt(3), y-r))
        vertices.append((x-r/math.sqrt(3), y-r))
        return vertices

        
# vertices = [(12, -9), (-12, -9), (-12, 20)]
# anc = Anchorage(vertices)
# # vessel = Vessel(3)
# # vessel2 = Vessel(2, (-10.0, 14.446411629213546))
# # anc.anchored.append(vessel2)
# anc.anchored.append(Vessel(2, (-10, 5)))
# print(areaMaxInscribedCircle(anc))


# print(checkVesselInside(anc.edges, -7.64696316941158, 10.034697940192649, 3))
# for ship in anc.anchored:
#     x1, y1 = ship.centre
#     print(x1, y1, ship.radius)
#     print(checkCircleCollision(x1, -7.64696316941158, y1, 10.034697940192649, ship.radius, 3))
# cp = anc.generateCornerPoints(vessel)
# print(cp)
# print(anc.isVesselInside(vessel))
# print(vessel.collidesWith(Vessel(2, (-10, 5))))
            