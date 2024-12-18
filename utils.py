import math

DEPTH = 35
# EXTRA_LENGTH = math.sqrt((25*math.sqrt(DEPTH)) ** 2 - DEPTH**2)
EXTRA_LENGTH = 0

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
        return edges
    
def checkVesselInside(edges, x, y, radius):
    for edge in edges:
        a, b, c = edge
        # check if centre of circle is inside boundary
        if a*x + b*y >= c:
            return False
        # check if circle intersects edge twice
        # if perp. dist between edge and circle is smaller than radius, means the edge is too close to the centre of the circle
        dist = abs(a*x + b*y - c)/math.sqrt(a**2 + b**2)
        # print(dist)
        if dist < radius:
            return False
    return True

def checkCircleCollision(x1, x2, y1, y2, r1, r2):
    # print(x1, x2, y1, y2, r1, r2)
    dist = math.sqrt((x1-x2) ** 2 + (y1-y2)**2)
    # print(dist, r1+r2)
    if dist >= r1 + r2:
        return False
    else: return True