from classes import *
from utils import *
import data_generator
from data_generator import dwell_times, boundaries, dwell_time_raw_data, obtain_ideal_distance, LIMIT
from copy import deepcopy

data_generator.instantiate_times()
# print(times[0])
# data_generator.obtain_ideal_distance(243.22)

LOOK_UP_TIME = 60 * 6 # 6 hours

class QueueNode:
    def __init__(self, anchorage, total = {'r': 0.0, 'u': [], 'd': 0.0, 't': 0.0}, metric_score = np.array([0.0] * 6), anchorSpots = {}, waiting = []):
        self.anchorage = anchorage
        self.total = total
        self.anchorSpots = anchorSpots
        self.waiting = waiting
        # 1. arrival intersection length (as a percentage of 2500)
        # 2. expected departure intersection length/2500 (based off vessels that are a. currently anchored b. will still be anchored at departure time)
        # 3. (distance between centre of anchor point and ideal anchor distance)/(maximum possible deviation distance)
        # 4. minimise normalised distance to entry
        # 5. minimise time waited/total time
        # 6. maximise, area of largest possible circle that can be inscribed/total area -> minimise 1 - ratio
        
        # from these, obtain a weighted score (out of 100). 
        # each vessel will contribute a score. take the average over number of vessels so far to compute node with lowest overall score
        self.metric_score = metric_score

class AnchoragePlanner:
    def __init__(self):
        
        self.queue = []
        self.time_list = []
        
        self.assignment = {}
        
        #list of all vessels
        self.vessels = {}
        
        # synthetic: [(2000, 1250), (2000, -1250), (-2000, -1250), (-2000, 1250)]
        self.anchorage = Anchorage([(2000.0, 1250.0), (2000.0, -1250.0), (-2000.0, -1250.0), (-2000.0, 1250.0)])
        
        # append an empty anchorage to the processing queue at the start 
        self.queue.append((0, QueueNode(self.anchorage)))
        
    def populate_time_list(self, data):
        for i, row in enumerate(data):
            arrival, departure, length = row
            self.time_list.append((arrival, 1, i+1))
            self.time_list.append((departure, -1, i+1))
            self.vessels[i+1] = Vessel(length, arrival=arrival, departure=departure, number=i+1)
        self.time_list.sort()
        
    def run_main(self):
        
        if len(self.time_list) == 0:
            return
        
        currTime = self.time_list[0][0]
        look_up_time = currTime + LOOK_UP_TIME
        leftIndex, rightIndex = 0, 0
        numVessels = 0
        
        while leftIndex < len(self.time_list):
            if leftIndex > rightIndex or (leftIndex == rightIndex and self.time_list[leftIndex][1] == -1):
                if self.time_list[leftIndex][1] == 1: # new arrival
                    rightIndex = leftIndex
                    currTime = self.time_list[leftIndex][0]
                    look_up_time = currTime + LOOK_UP_TIME
                    continue
                
                # unseen departure that must be handled now
                time, vesselNumber = self.time_list[leftIndex][0], self.time_list[leftIndex][2]
                for _ in range(len(self.queue)):
                    ogScore, qNode = self.queue.pop(0)
                    anc, total, metrics = qNode.anchorage, qNode.total, qNode.metric_score
                    ancSpots = qNode.anchorSpots
                    
                    # if the vessel is still in the waiting list
                    waitingSet = set([ship.number for ship in qNode.waiting])
                    if vesselNumber in waitingSet:
                        self.amendTotal(time, qNode.total, t = vessel.departure - vessel.arrival)
                        qNode.anchorSpots[vesselNumber] = None
                        self.queue.append((ogScore, qNode))
                        continue
                    
                    vessel2 = [ship for ship in anc.anchored if ship.number == vesselNumber][0]
                    anc.anchored.remove(vessel2)
                    DID, _  = calculateIntersectionDistance(vessel2, anc.anchored, vessel2.centre[0], vessel2.centre[1], calculateDID=False)
                    NDE = calculateNDE(vessel2.centre[0], vessel2.centre[1], anc) # normalised distance to exit
                    area = areaMaxInscribedCircle(anc)
                    self.amendTotal(time, qNode.total, d = NDE, r = DID, area=area)
                    
                    # check if any waiting vessels can be added
                    temp_list = [(ogScore, qNode, 0)]
                    final_list = []
                    if len(qNode.waiting) > 0:
                        self.addWaitingVessels(numVessels, time, temp_list, final_list)
                    else:
                        final_list = [(ogScore, qNode)]
                            
                    # extend queue with all nodes generated in temporary list
                    self.queue.extend(final_list)
                leftIndex +=1
                continue
                    
            # while you can still look ahead        
            while rightIndex < len(self.time_list) and self.time_list[rightIndex][0] <= look_up_time: 
                time, vesselNumber = self.time_list[rightIndex][0], self.time_list[rightIndex][2]
                departing = True if self.time_list[rightIndex][1] == -1 else False # departure of an existing vessel
                vessel = self.vessels[vesselNumber]
                
                if not departing: # arrival
                    numVessels += 1
                    
                for _ in range(len(self.queue)): # expand all existing queue nodes with incoming vessel
                    #needed even for departure as departure may allow vessels in waiting queue to enter anchorage
                    ogScore, qNode = self.queue.pop(0)
                    print(len(self.queue))
                    anc, total, metrics = qNode.anchorage, qNode.total, qNode.metric_score
                    ancSpots = qNode.anchorSpots
                    
                    if departing:
                        # if the vessel is still in the waiting list
                        waitingSet = set([ship.number for ship in qNode.waiting])
                        if vesselNumber in waitingSet:
                            self.amendTotal(time, qNode.total, t = vessel.departure - vessel.arrival)
                            qNode.anchorSpots[vesselNumber] = None
                            self.queue.append((ogScore, qNode))
                            continue
                        
                        # vessel is in anchorage
                        vessel2 = [ship for ship in anc.anchored if ship.number == vesselNumber][0]
                        anc.anchored.remove(vessel2)
                        DID, _  = calculateIntersectionDistance(vessel2, anc.anchored, vessel2.centre[0], vessel2.centre[1], calculateDID=False)
                        NDE = calculateNDE(vessel2.centre[0], vessel2.centre[1], anc) # normalised distance to exit
                        area = areaMaxInscribedCircle(anc)
                        self.amendTotal(time, qNode.total, d = NDE, r = DID, area=area)
                        
                        # check if any waiting vessels can be added
                        temp_list = [(ogScore, qNode, 0)]
                        final_list = []
                        if len(qNode.waiting) > 0:
                            self.addWaitingVessels(numVessels, time, temp_list, final_list)
                        else:
                            final_list = [(ogScore, qNode)]
                                
                        # extend queue with all nodes generated in temporary list
                        self.queue.extend(final_list)
                        continue
                    
                    # arriving vessel - generate corner points
                    cornerPoints = qNode.anchorage.generateCornerPoints(vessel)
                    
                    if len(cornerPoints) == 0: # no place for incoming vessel:
                        # append vessel to waiting queue of queue node, update score, and add node back into queue
                        qNode.waiting.append(vessel)
                        indivScore = [0] * 6
                        indivScore[4] = 100 # at the moment worst case estimate is that it is unable to anchor inside for the full duration
                        qNode.metric_score = np.add(qNode.metric_score, indivScore)
                        score = calculateScore(qNode.metric_score, numVessels)
                        qNode.anchorSpots[vesselNumber] = None
                        self.queue.append((score, qNode))
                        continue
                    
                    for cornerPoint in cornerPoints:
                        print(vesselNumber, cornerPoint)
                        NDE, AID, indivScore = self.calcDistanceMetrics(time, vessel, anc, cornerPoint)
                        
                        # 5. minimise time waited/total time
                        # waiting time is zero since it is able to anchor inside immediately
                        indivScore[4] = 0
                        
                        # 6. maximise, area of largest possible circle that can be inscribed/total area -> minimise 1 - ratio
                        anc2 = deepcopy(anc)
                        vessel2 = deepcopy(vessel)
                        vessel2.centre = cornerPoint
                        anc2.anchored.append(vessel2)
                        area = areaMaxInscribedCircle(anc2)
                        indivScore[5] = 100 * (1 - area/anc2.area)
                        
                        # wrap up and add this as a new queue node in the queue
                        metric2 = np.add(metrics, indivScore)
                        spots2 = deepcopy(ancSpots)
                        spots2[vesselNumber] = cornerPoint
                        total2 = deepcopy(total)
                        self.amendTotal(time, total2, d = NDE, r = AID, area = area)
                        score = calculateScore(metric2, numVessels)
                        self.queue.append((score, QueueNode(anc2, total2, metric2, spots2, deepcopy(qNode.waiting))))
                rightIndex += 1
            
            # pull back rightIndex by 1 if time of rightIndex is beyond look_up_time
            # if rightIndex < len(self.time_list) and self.time_list[rightIndex][0] > look_up_time:
            #     rightIndex -= 1
                
            # maximum look ahead reached
            # prune queue based off score
            # if any previously waiting vessels have been admitted, take note of their assignments in the node with the best score
            # and only keep nodes whose assignments agree
            
            self.queue.sort(key = lambda x: x[0])
            currIncomingVesselNumber = self.time_list[leftIndex][2]
            bestNode = self.queue[0][1]
            bestCoordinates = [(bestNode.anchorSpots[currIncomingVesselNumber], currIncomingVesselNumber)]
            
            # list of vessels in best scoring node, with vessel number less than incoming vessel number, unsettled assignment, but is not in waiting list of said node anymore
            for k in range(1, currIncomingVesselNumber):
                if k in self.assignment and self.assignment[k] is not None:
                    continue
                if k in bestNode.anchorSpots and bestNode.anchorSpots[k] is not None:
                    bestCoordinates.append((bestNode.anchorSpots[k], k))
            
            for coordinate, admVesselNumber in bestCoordinates:
                self.assignment[admVesselNumber] = coordinate
            self.pruneQueue(bestCoordinates)
            
            
            # at this point, right index is beyond the current look-up-time and is unseen
            leftIndex += 1
            while leftIndex < rightIndex:
                if leftIndex >= len(self.time_list): # edge-case where left exceeds length of list
                    break
                if self.time_list[leftIndex][1] == 1: # next incoming vessel needs to be settled 
                    currTime = self.time_list[leftIndex][0]
                    look_up_time = currTime + LOOK_UP_TIME
                    break
                # departure that should have been handled by right index already
                leftIndex += 1
        
        self.queue.sort(key = lambda x: x[0])
        bestNode = self.queue[0][1]
        return bestNode.total, bestNode.anchorSpots, self.assignment

    def addWaitingVessels(self, numVessels, time, temp_list, final_list):
        while len(temp_list) > 0:
            score, currNode, j = temp_list.pop(0)                
            waitVessel, cornerPoints = None, []
            
            while j < len(currNode.waiting):
                waitVessel = currNode.waiting[j]
                cornerPoints = currNode.anchorage.generateCornerPoints(waitVessel)
                if len(cornerPoints) != 0:
                    break
                j += 1
            
            if j >= len(currNode.waiting): # processed all waiting vessels in this node
                final_list.append((score, currNode))
                continue
            
            ogContribution = np.array([0.0] * 6)
            ogContribution[4] = 100
            # eliminate original contribution by waiting vessel
            currNode.metric_score = np.subtract(currNode.metric_score, ogContribution)
            # indivScore = np.array([0.0] * 6)
                            
            for cornerPoint in cornerPoints:
                NDE, AID, indivScore = self.calcDistanceMetrics(time, waitVessel, currNode.anchorage, cornerPoint)
                                
                # 5. minimise time waited/total time
                indivScore[4] = (time - waitVessel.arrival)/(waitVessel.departure - waitVessel.arrival) * 100
                                
                # 6. maximise, area of largest possible circle that can be inscribed/total area -> minimise 1 - ratio
                currNodeCopy = deepcopy(currNode)
                waitVesselCopy = deepcopy(waitVessel)
                                
                currNodeCopy.anchorage.anchored.append(waitVesselCopy)
                waitVesselCopy.centre = cornerPoint
                area = areaMaxInscribedCircle(currNodeCopy.anchorage)
                indivScore[5] = 100 * (1 - area/currNodeCopy.anchorage.area)
                                
                currNodeCopy.waiting.pop(j)
                currNodeCopy.metric_score = np.add(currNodeCopy.metric_score, indivScore)
                new_score = calculateScore(currNodeCopy.metric_score, numVessels)
                currNodeCopy.anchorSpots[waitVesselCopy.number] = cornerPoint
                self.amendTotal(time, currNodeCopy.total, d = NDE, r = AID, area=area, t = time - waitVesselCopy.arrival)
                temp_list.append((new_score, currNodeCopy, j))
      
        
    def pruneQueue(self, bestCoordinates):
        print('pruning reached')
        newQueue = []
        for score, node in self.queue:
            canBeAdded = True
            for bestCoordinate, vesselNumber in bestCoordinates:
                if bestCoordinate is None:
                    if node.anchorSpots[vesselNumber] is not None:
                        canBeAdded = False
                        break
                if node.anchorSpots[vesselNumber] is None:
                    canBeAdded = False
                    break
                x, y = node.anchorSpots[vesselNumber]
                if abs(bestCoordinate[0] - x) > 0.1 or abs(bestCoordinate[1] - y) > 0.1:
                    canBeAdded = False
            if canBeAdded:
                newQueue.append((score, node))
        self.queue = newQueue
            

    def calcDistanceMetrics(self, time, vessel, anc, cornerPoint):
        anc_vessels = anc.anchored
        x, y = cornerPoint
        indivScore = np.array([0.0] * 6)
                    
        # 1. arrival intersection length (as a percentage of 2500)
        # 2. expected departure intersection length/2500 (based off vessels that are a. currently anchored b. will still be anchored at departure time)
        AID, EDID = calculateIntersectionDistance(vessel, anc_vessels, x, y)
        indivScore[0] = AID/MAX_WIDTH * 100
        indivScore[1] = EDID/MAX_WIDTH * 100
        
        # print(obtain_ideal_distance(vessel.departure - time))                
        # 3. (difference in distance between centre of anchor point and entry line (max width/2 assuming anchorage is centred around origin) and ideal anchor distance)/(maximum possible deviation distance)
        indivScore[2] = abs((MAX_WIDTH/2 - y) - obtain_ideal_distance(vessel.departure - time))/(MAX_IDEAL_DIST - MIN_IDEAL_DIST) * 100
                    
        # 4. minimise normalised distance to entry
        NDE = calculateNDE(x, y, anc)
        indivScore[3] = NDE/MAX_WIDTH * 100
        return NDE, AID, indivScore

    def amendTotal(self, time, total, d = None, r = None, area = None, t = None):
        if time < 0:
            return
        if d is not None:
            total['d'] += d
        if r is not None:
            total['r'] += r
        if area is not None:
            total['u'].append((time, area))
        if t is not None:
            total['t'] += t

anchorage_name = 'Synthetic Anchorage (normal)'
raw_data = data_generator.read_data(anchorage_name)
sample = raw_data['1']

# # sample = [(60, 600, 856), (120, 800, 456), (180, 700, 606), (240, 750, 306), (450, 900, 606)]
# sample = [(60, 480, 856), (490, 800, 456), (520, 700, 606), (600, 750, 306), (650, 1000, 606)]
# print(sample)

anc_planner = AnchoragePlanner()
anc_planner.populate_time_list(sample)
# totals, nodeAssignment, plannerAssignment = anc_planner.run_main()
# print(totals, nodeAssignment, plannerAssignment, sep='\n')
# print(time_list)


