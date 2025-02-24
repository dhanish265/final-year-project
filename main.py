from classes import *
from utils import *
import data_generator
from data_generator import dwell_times, boundaries, dwell_time_raw_data, obtain_ideal_distance, LIMIT, write_to_xlsx
from copy import deepcopy
import time as tm
import math
from data_generator import LOWER_LIMIT, UPPER_LIMIT

data_generator.instantiate_times()
# print(times[0])
# data_generator.obtain_ideal_distance(243.22)

LOOK_UP_TIME = 60 * 6 # 6 hours

class QueueNode:
    def __init__(self, anchorage, total=None, metric_score=None, anchorSpots=None, waiting=None):
        if total is None:
            total = [{'time': 0, 'd': [0, 0], 'ra': [0, 0], 'rd': [0, 0], 'area': areaMaxInscribedCircle(anchorage), 't': [0, 0], 'util': 0}]
        if metric_score is None:
            metric_score = np.array([0.0] * 6)
        if anchorSpots is None:
            anchorSpots = {}
        if waiting is None:
            waiting = []
        
        self.anchorage = anchorage
        self.total = total
        self.anchorSpots = anchorSpots
        self.waiting = waiting
        self.metric_score = metric_score
        # 1. arrival intersection length (as a percentage of 2500)
        # 2. expected departure intersection length/2500 (based off vessels that are a. currently anchored b. will still be anchored at departure time)
        # 3. (distance between centre of anchor point and ideal anchor distance)/(maximum possible deviation distance)
        # 4. minimise normalised distance to entry
        # 5. minimise time waited/total time
        # 6. maximise, area of largest possible circle that can be inscribed/total area -> minimise 1 - ratio
        
        # from these, obtain a weighted score (out of 100). 
        # each vessel will contribute a score. take the average over number of vessels so far to compute node with lowest overall score

class AnchoragePlanner:    
    def __init__(self, standard = True, busyStatus = 'normal'):
        
        self.busyStatus = busyStatus
        self.queue = []
        self.time_list = []
        
        self.assignment = {}
        
        #list of all vessels
        self.vessels = {}
        
        # synthetic: [(2000, 1250), (2000, -1250), (-2000, -1250), (-2000, 1250)]
        if standard:
            self.anchorage = Anchorage([(2000.0, 1250.0), (2000.0, -1250.0), (-2000.0, -1250.0), (-2000.0, 1250.0)])
        else:
            self.anchorage = Anchorage([(-250.0, 990.0), (-2000.0 ,310.0), (-2000.0, -1250.0), (2000.0, -310.0), (2000.0, 1250.0)])
        
        # append an empty anchorage to the processing queue at the start 
        self.queue.append((0, QueueNode(self.anchorage)))
        pass
        
    def populate_time_list(self, data):
        for i, row in enumerate(data):
            arrival, departure, length = row
            self.time_list.append((arrival, 1, i+1))
            self.time_list.append((departure, -1, i+1))
            self.vessels[i+1] = Vessel(length, arrival=arrival, departure=departure, number=i+1)
        self.time_list.sort()
        # print(self.time_list)
        
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
                
                # unseen departure that must be handled now - ties to line 231, else: self.cleanUp(bestNode)
                time, vesselNumber = self.time_list[leftIndex][0], self.time_list[leftIndex][2]
                for _ in range(len(self.queue)):
                    ogScore, qNode = self.queue.pop(0)
                    anc, total, metrics = qNode.anchorage, qNode.total, qNode.metric_score
                    ancSpots = qNode.anchorSpots
                    
                    # if the vessel is still in the waiting list
                    waitingSet = set([ship.number for ship in qNode.waiting])
                    if vesselNumber in waitingSet:
                        pos = [i for i in range(len(qNode.waiting)) if qNode.waiting[i].number == vesselNumber][0]
                        vessel = qNode.waiting.pop(pos)
                        self.amendTotal(time, qNode.total, t = max(0, min(vessel.departure, UPPER_LIMIT) - max(vessel.arrival, LOWER_LIMIT)), vessel=vessel)
                        qNode.anchorSpots[vesselNumber] = None
                        self.queue.append((ogScore, qNode))
                        continue
                    
                    # handle departing vessel
                    self.handleDepartingAnchoredVessel(time, vesselNumber, qNode, anc)
                    
                    # check if any waiting vessels can be added
                    temp_list = [(ogScore, qNode, 0)]
                    final_list = []
                    if len(qNode.waiting) > 0:
                        self.addWaitingVessels(numVessels, time, temp_list, final_list)
                    else:
                        final_list = [(ogScore, qNode)]
                            
                    # extend queue with all nodes generated in temporary list
                    self.queue.extend(final_list)
                    
                
                # self.pruneQueue()
                    
                # amend here
                # leftIndex +=1
                # continue
                    
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
                            pos = [i for i in range(len(qNode.waiting)) if qNode.waiting[i].number == vesselNumber][0]
                            qNode.waiting.pop(pos)
                            self.amendTotal(time, qNode.total, t = max(0, min(vessel.departure, UPPER_LIMIT) - max(vessel.arrival, LOWER_LIMIT)), vessel=vessel)
                            qNode.anchorSpots[vesselNumber] = None
                            self.queue.append((ogScore, qNode))
                            continue
                        
                        # vessel is in anchorage
                        self.handleDepartingAnchoredVessel(time, vesselNumber, qNode, anc)
                        
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
                    
                    temp_queue = []
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
                        self.amendTotal(time, total2, d = NDE, ra = AID, area = area, t = 0, util = math.pi * vessel2.radius ** 2)
                        score = calculateScore(metric2, numVessels)
                        temp_queue.append((score, QueueNode(anc2, total2, metric2, spots2, deepcopy(qNode.waiting))))
                    temp_queue.sort(key = lambda x: x[0])
                    temp_queue = temp_queue[:EXPANSION_SIZE]
                    # print('temp', temp_queue)
                    self.queue.extend(temp_queue)
                    
                self.pruneQueue()
                rightIndex += 1
            
                
            # maximum look ahead reached
            # fix incoming vessel based off score
            # if any previously waiting vessels have been admitted, take note of their assignments in the node with the best score
            # and only keep nodes whose assignments agree
            
            self.queue.sort(key = lambda x: x[0])
            bestNode = self.queue[0][1]
            
            if self.time_list[leftIndex][1] == 1:
                currIncomingVesselNumber = self.time_list[leftIndex][2]
                self.cleanUp(bestNode, currIncomingVesselNumber)
                
            else: #unseen departure, left is beyond right, all incoming vessels thus far should have been anchored/waiting
                self.cleanUp(bestNode)
                
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
                # must eliminate inconsistent nodes, 
                # with respect to vessels that may have entered upon departure of this vessel
                # as we are now confirming the departure of this vessel in real-time
                
                self.queue.sort(key = lambda x: x[0])
                bestNode = self.queue[0][1]
                self.cleanUp(bestNode, currIncomingVesselNumber)
                leftIndex += 1
        
        self.queue.sort(key = lambda x: x[0])
        bestNode = self.queue[0][1]
        return bestNode.total, bestNode.anchorSpots, self.assignment

    def cleanUp(self, bestNode, currIncomingVesselNumber = None):
        bestCoordinates = []
                
        # list of vessels in best scoring node, with vessel number less than incoming vessel number, 
        # unsettled assignment, but is not in waiting list of said node anymore
        if currIncomingVesselNumber is not None:
            bestCoordinates.append((bestNode.anchorSpots[currIncomingVesselNumber], currIncomingVesselNumber))
            for k in range(1, currIncomingVesselNumber):
                if k in self.assignment and self.assignment[k] is not None:
                    continue
                if k in bestNode.anchorSpots and bestNode.anchorSpots[k] is not None:
                    bestCoordinates.append((bestNode.anchorSpots[k], k))
        else:
            for k in self.assignment: 
                if self.assignment[k] is not None: # already permanently assigned and hence irrelevant
                    continue
                # not permanently assigned, but best node has somehow managed to remove it from waiting list
                if k in bestNode.anchorSpots and bestNode.anchorSpots[k] is not None:
                    bestCoordinates.append((bestNode.anchorSpots[k], k))
                
        if len(bestCoordinates) > 0:
            for coordinate, vesselNumber in bestCoordinates:
                self.assignment[vesselNumber] = coordinate
            self.eliminateInconsistentNodes(bestCoordinates)
            self.pruneQueue()

    def pruneQueue(self):
        if len(self.queue) > BEAM_LENGTH:
            self.queue.sort(key = lambda x: x[0])
            self.queue = self.queue[:BEAM_LENGTH]

    def handleDepartingAnchoredVessel(self, time, vesselNumber, node, anc):
        vessel2 = [ship for ship in anc.anchored if ship.number == vesselNumber][0]
        anc.anchored.remove(vessel2)
        DID, _  = calculateIntersectionDistance(vessel2, anc.anchored, vessel2.centre[0], vessel2.centre[1], calculateDID=False)
        NDE = calculateNDE(vessel2.centre[0], vessel2.centre[1], anc) # normalised distance to exit
        area = areaMaxInscribedCircle(anc)
        self.amendTotal(time, node.total, d = NDE, rd = DID, area=area, util = -math.pi * vessel2.radius ** 2)
    
    def run_alternate(self, method = 'NDE', SPSA_weight_setting = 0):
        if len(self.time_list) == 0:
            # modify later once confirmed
            return
        
        numVessels = 0
        node = self.queue[0][1]
        for index in range(len(self.time_list)):
            time, departing, vesselNumber = self.time_list[index]
            vessel = self.vessels[vesselNumber]
            departing = True if departing == -1 else False
            
            if departing:
                waitingSet = set([ship.number for ship in node.waiting])
                if vesselNumber in waitingSet:
                    pos = [i for i in range(len(node.waiting)) if node.waiting[i].number == vesselNumber][0]
                    node.waiting.pop(pos)
                    self.amendTotal(time, node.total, t = max(0, min(vessel.departure, UPPER_LIMIT) - max(vessel.arrival, LOWER_LIMIT)), vessel=vessel)
                    self.assignment[vesselNumber] = None
                    node.anchorSpots[vesselNumber] = None
                    continue
                
                # vessel is in anchorage
                self.handleDepartingAnchoredVessel(time, vesselNumber, node, node.anchorage)
                #check if any waiting vessels can be admitted
                i = 0
                while i < len(node.waiting):
                    waitVessel = node.waiting[i]
                    cornerPoints = node.anchorage.generateCornerPoints(waitVessel)
                    if len(cornerPoints) == 0:
                        i += 1
                        continue
                    
                    node.waiting.pop(i)
                    waitVessel.waitTime = time - waitVessel.arrival
                    # self.amendTotal(time, node.total, t = time - waitVessel.arrival)
                    self.alternateAnchoringProcess(method, node, time, waitVessel, cornerPoints, SPSA_weight_setting)   
                continue
            
            # arriving vessel
            numVessels += 1
            cornerPoints = node.anchorage.generateCornerPoints(vessel)
            
            if len(cornerPoints) == 0:
                node.waiting.append(vessel)
                node.anchorSpots[vesselNumber] = None
                continue
            self.alternateAnchoringProcess(method, node, time, vessel, cornerPoints, SPSA_weight_setting)
        
        return node.total, node.anchorSpots, self.assignment

    def alternateAnchoringProcess(self, method, node, time, vessel, cornerPoints, SPSA_weight_setting):
        rankList = []
        for cornerPoint in cornerPoints:
            x, y = cornerPoint
            if method == 'NDE':
                NDE = calculateNDE(x, y, node.anchorage)
                rankList.append((NDE, cornerPoint))
            elif method == 'MHD':
                holeDegree = node.anchorage.calculateHoleDegree(cornerPoint, vessel.radius)
                rankList.append((holeDegree, cornerPoint))
            elif method == 'SPSA':
                AID, EDID = calculateIntersectionDistance(vessel, node.anchorage.anchored, x, y, calculateDID=True)
                NDE = calculateNDE(x, y, node.anchorage)
                dwell = vessel.departure - time
                scores = [AID, EDID, NDE, dwell * AID, dwell * EDID, dwell * NDE, dwell * AID * EDID]
                score = -np.dot(np.array(scores), SPSA_WEIGHTS[SPSA_weight_setting]) 
                # since this is to be minimised in the original algorithm, 
                # the negative is taken to be consistent with the maximisation of the other 2 algorithms
                rankList.append((score, cornerPoint))
            
        rankList.sort(key = lambda x: x[0], reverse=True)
        x, y = rankList[0][1]
        AID, _ = calculateIntersectionDistance(vessel, node.anchorage.anchored, x, y, calculateDID=False)
        NDE = calculateNDE(x, y, node.anchorage)
        node.anchorage.anchored.append(vessel)
        vessel.centre = (x, y)
        node.anchorSpots[vessel.number] = (x, y)
        area = areaMaxInscribedCircle(node.anchorage)
        self.amendTotal(time, node.total, d = NDE, ra= AID, area=area, util = math.pi * vessel.radius ** 2, t = max(0, min(time, UPPER_LIMIT) - max(vessel.arrival, LOWER_LIMIT)), vessel=vessel)
        self.assignment[vessel.number] = (x, y)


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
            
            temp_list2 = []
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
                self.amendTotal(time, currNodeCopy.total, d = NDE, ra = AID, area=area, t = max(0, min(UPPER_LIMIT, time) - max(LOWER_LIMIT, waitVesselCopy.arrival)), util = math.pi * waitVessel.radius ** 2, vessel=waitVesselCopy)
                temp_list2.append((new_score, currNodeCopy, j))
            
            temp_list2.sort(key=lambda x: x[0])
            if len(temp_list2) > EXPANSION_SIZE:
                temp_list2 = temp_list2[:EXPANSION_SIZE]
            temp_list.extend(temp_list2)
      
        
    def eliminateInconsistentNodes(self, bestCoordinates):
        print('elimination reached')
        newQueue = []
        for score, node in self.queue:
            canBeAdded = True
            for bestCoordinate, vesselNumber in bestCoordinates:
                if bestCoordinate is None:
                    if node.anchorSpots[vesselNumber] is not None:
                        canBeAdded = False
                        break
                    continue
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
        indivScore[2] = abs((MAX_WIDTH/2 - y) - obtain_ideal_distance(vessel.departure - time, self.busyStatus))/(MAX_IDEAL_DIST - MIN_IDEAL_DIST) * 100
                    
        # 4. minimise normalised distance to entry
        NDE = calculateNDE(x, y, anc)
        indivScore[3] = NDE/MAX_WIDTH * 100
        return NDE, AID, indivScore

    def amendTotal(self, time, total, d = None, ra = None, rd = None, area = None, t = None, util = None, vessel = None):
        
        entry = deepcopy(total[-1])
        
        if time > UPPER_LIMIT:
            if total[-1]['time'] < UPPER_LIMIT:
                entry['time'] = time
            if t is not None and vessel is not None and vessel.arrival < UPPER_LIMIT:
                entry['t'][0] += t
                entry['t'][1] += 1
                total.append(entry)
            return
        
        entry['time'] = time
        if time < LOWER_LIMIT:
            if area is not None:
                entry['area'] = area
            if util is not None:
                entry['util'] += util
            total.append(entry)
            total.pop(0)
            return
            
        if area is not None:
            entry['area'] = area
        if util is not None:
            entry['util'] += util
        if d is not None:
            entry['d'][0] += d
            entry['d'][1] += 1
        if ra is not None:
            entry['ra'][0] += ra
            entry['ra'][1] += 1
        if rd is not None:
            entry['rd'][0] += rd
            entry['rd'][1] += 1
        if t is not None:
            entry['t'][0] += t
            entry['t'][1] += 1
        total.append(entry)
        

anchorage_names = ['Synthetic Anchorage (normal)', 'Synthetic Anchorage (busy)', 'Synthetic Anchorage (idle)', 'Ahirkapi Anchorage']
# anchorage_names = ['Ahirkapi Anchorage'] 
# anchorage_names = ['Synthetic Anchorage (idle)', 'Ahirkapi Anchorage']   
def run():
    # anchorage_name = 'Synthetic Anchorage (normal)'
    # raw_data = data_generator.read_data(anchorage_name)
    # return 1, 2
    
    # samples = []
    # samples.append([(60, 600, 856), (120, 800, 456), (180, 700, 606), (240, 750, 306), (450, 900, 606)])
    # samples.append([(60, 480, 856), (490, 800, 456), (520, 700, 606), (600, 750, 306)])
    # print(sample)
    
    i = 21
    
    for anchorage_name in anchorage_names:
        data = []
        raw_data = data_generator.read_data(anchorage_name)
        
        for j in range(1):
            # for i in range(16, 21):
                sample = raw_data[str(i)]
                if 'busy' in anchorage_name:
                    busyStatus = 'busy'
                elif 'idle' in anchorage_name:
                    busyStatus = 'idle'
                else: busyStatus = 'normal'
                
                if 'Ahirkapi' in anchorage_name:
                    anc_planner = AnchoragePlanner(standard=False, busyStatus=busyStatus)
                else:
                    anc_planner = AnchoragePlanner(standard=True, busyStatus=busyStatus)
                    
                area = areaMaxInscribedCircle(anc_planner.anchorage)
                anc_planner.populate_time_list(sample)
                print(anc_planner.time_list[0])
                start_time = tm.ctime(tm.time())
                totals, nodeAssignment, plannerAssignment = anc_planner.run_main()
                # totals, nodeAssignment, plannerAssignment = anc_planner.run_alternate(method='SPSA', SPSA_weight_setting=j)
                for total in totals:
                    print(total)
                end_time = tm.ctime(tm.time())
                print(start_time, end_time)
                utilavg = obtainAverageArea(totals, area, UPPER_LIMIT, LOWER_LIMIT, param='area')
                remavg = obtainAverageArea(totals, anc_planner.anchorage.area, UPPER_LIMIT, LOWER_LIMIT, param='util')
                risk = (totals[-1]['ra'][0]/totals[-1]['ra'][1] + totals[-1]['rd'][0]/totals[-1]['rd'][1])/2
                dist = totals[-1]['d'][0]/totals[-1]['d'][1]
                time = totals[-1]['t'][0]/totals[-1]['t'][1]
                
                data.append((risk, dist, time, remavg, utilavg))
                data.append((start_time, end_time))
        write_to_xlsx([data], 'temp_ + ' + anchorage_name + '.xlsx', ['data'])
    
run()



