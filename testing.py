import classes
import data_generator
import utils
import main_testing_copy

standard = classes.Anchorage([(2000.0, 1250.0), (2000.0, -1250.0), (-2000.0, -1250.0), (-2000.0, 1250.0)])
ahirkapi = classes.Anchorage([(-250.0, 990.0), (-2000.0 ,310.0), (-2000.0, -1250.0), (2000.0, -310.0), (2000.0, 1250.0)])


""" 
# case 1a)
vessel = classes.Vessel(200)
print(standard.generateCornerPoints(vessel))
print(ahirkapi.generateCornerPoints(vessel)) """

 
"""
# case 1b)
vessel, vessel1, vessel2 = classes.Vessel(100), classes.Vessel(200, centre=(-1658.298, -816.16)), classes.Vessel(200, centre=(-1658.298, 74.815))
ahirkapi.anchored.append(vessel1)
ahirkapi.anchored.append(vessel2)
print(ahirkapi.generateCornerPoints(vessel))
vessel, vessel1, vessel2 = classes.Vessel(300), classes.Vessel(300, centre=(-1558.298, -806.298)), classes.Vessel(300, centre=(-1558.298, 806.298))
standard.anchored.append(vessel1)
standard.anchored.append(vessel2)
print(standard.generateCornerPoints(vessel))
 """
 
""" 
# case 1c)
info = [((-1256.298, 506.298), 600), ((-166.75, -506.298), 600), ((925.298, 506.298), 600), ((1366.75, -706.298), 403), ((-1476.75, -730.298), 363)]
for centre, length in info:
    standard.anchored.append(classes.Vessel(length=length, centre=centre))
print('cornerpoints = ', standard.generateCornerPoints(classes.Vessel(300)))
info = [((-90.920, 401.504), 450), ((-1256.298, -316.16), 600), ((1256.298, 296.929), 600)]
for centre, length in info:
    ahirkapi.anchored.append(classes.Vessel(length=length, centre=centre))
print('cornerpoints = ', ahirkapi.generateCornerPoints(classes.Vessel(300))) """

""" 
# case 1d)
info = [((-40, 0), 300), ((-1360, 0), 300), ((-700, 400), 187), ((-420, -600), 117), ((-980, -650), 157)]
for centre, length in info:
    ahirkapi.anchored.append(classes.Vessel(length=length, centre=centre))
print(ahirkapi.generateCornerPoints(classes.Vessel(96)))
print()
info = [((887.4, 0), 300), ((-887.4, 0), 300), ((443.7, 776.475), 300), ((-443.7, 776.475), 300), ((443.7, -776.475), 300), ((-443.7, -776.475), 300)]
for centre, length in info:
    standard.anchored.append(classes.Vessel(length=length, centre=centre))
print(standard.generateCornerPoints(classes.Vessel(300))) """

"""
# case 2a)
print(utils.areaMaxInscribedCircle(standard))
print(utils.areaMaxInscribedCircle(ahirkapi)) """

""" 
# case 2b)
info = [((750, 0), 1250-utils.EXTRA_LENGTH), ((-1500, -100), 500-utils.EXTRA_LENGTH)]
for centre, length in info:
    standard.anchored.append(classes.Vessel(length=length, centre=centre))
print(utils.areaMaxInscribedCircle(standard))
info = [((-32.226, 122.070), 885.5-utils.EXTRA_LENGTH), ((-1470, -40), 510-utils.EXTRA_LENGTH), ((1410, 200), 540-utils.EXTRA_LENGTH)]
for centre, length in info:
    ahirkapi.anchored.append(classes.Vessel(length=length, centre=centre))
print(utils.areaMaxInscribedCircle(ahirkapi)) """

"""
# case 3a)
vessel = classes.Vessel(500-utils.EXTRA_LENGTH)
print("arrival, departure = ", utils.calculateIntersectionDistance(vessel, standard.anchored, -1500, -750, True))
vessel = classes.Vessel(300-utils.EXTRA_LENGTH)
print("arrival, departure = ", utils.calculateIntersectionDistance(vessel, ahirkapi.anchored, -1690, -860, True)) """

""" 
# case 3b)
vessel1 = classes.Vessel(350-utils.EXTRA_LENGTH, centre=(-1650, 450), departure=500)
vessel2 = classes.Vessel(250-utils.EXTRA_LENGTH, centre=(-1400, 1000), departure=300)
vessel3 = classes.Vessel(230-utils.EXTRA_LENGTH, centre=(-1760, -1010), departure=600)
vessel = classes.Vessel(450-utils.EXTRA_LENGTH, departure=400)
standard.anchored.append(vessel1)
standard.anchored.append(vessel2)
standard.anchored.append(vessel3)
print('arrival, departure = ', utils.calculateIntersectionDistance(vessel, standard.anchored, -1550, -350, True))

vessel1 = classes.Vessel(200-utils.EXTRA_LENGTH, centre=(-1800, 170), departure=300)
vessel2 = classes.Vessel(270-utils.EXTRA_LENGTH, centre=(-1690, 290), departure=500)
vessel = classes.Vessel(300-utils.EXTRA_LENGTH, departure=400)
ahirkapi.anchored.append(vessel1)
ahirkapi.anchored.append(vessel2)
print('arrival, departure = ', utils.calculateIntersectionDistance(vessel, ahirkapi.anchored, -1690, -860, True)) """

""" 
# case 4a)
data_generator.instantiate_times()
print(data_generator.obtain_ideal_distance(5, 'busy'))
print(data_generator.obtain_ideal_distance(5, 'normal'))
print(data_generator.obtain_ideal_distance(5, 'idle')) """

""" 
# case 4b)
data_generator.instantiate_times()
print(data_generator.obtain_ideal_distance(2000, 'busy'))
print(data_generator.obtain_ideal_distance(2000, 'normal'))
print(data_generator.obtain_ideal_distance(2000, 'idle')) """

""" 
# case 4c)
data_generator.instantiate_times()
print(data_generator.obtain_ideal_distance(90000, 'busy'))
print(data_generator.obtain_ideal_distance(90000, 'normal'))
print(data_generator.obtain_ideal_distance(90000, 'idle'))
 """
 
""" 
# case 5a)
print(utils.calculateNDE(-1750, 1000, standard))
print(utils.calculateNDE(-1800, 173, ahirkapi))
print(utils.calculateNDE(-180, 695, ahirkapi))
print(utils.calculateNDE(1500, 688, ahirkapi)) """

""" 
# case 5b)
print(utils.calculateNDE(-1750, -1000, standard))
print(utils.calculateNDE(-1800, -997, ahirkapi))
print(utils.calculateNDE(-180, -512, ahirkapi))
print(utils.calculateNDE(1500, 88, ahirkapi)) """

""" 
# case 5c)
print(utils.calculateNDE(-1750, 0, standard))
print(utils.calculateNDE(-1300, 0, ahirkapi))
print(utils.calculateNDE(1100, 0, ahirkapi)) """


""" # case 6, 7 and 8)
# be sure to comment and uncomment the correct lines in the testing copy file to see the appropriate output
anc_planner = main_testing_copy.AnchoragePlanner()
data = [(60, 240, 1250-utils.EXTRA_LENGTH), (120, 300,750-utils.EXTRA_LENGTH), (180, 360, 750-utils.EXTRA_LENGTH)]
anc_planner.populate_time_list(data)
anc_planner.run_main()
 """

""" 
# case 9 and 11)
# be sure to comment and uncomment the correct lines in the testing copy file to see the appropriate output
anc_planner = main_testing_copy.AnchoragePlanner()
data = [(17900, 18400, 1000-utils.EXTRA_LENGTH), 
        (18100, 28000,750-utils.EXTRA_LENGTH), 
        (18300, 28200, 750-utils.EXTRA_LENGTH), 
        (28400, 28500, 500-utils.EXTRA_LENGTH)]
anc_planner.populate_time_list(data)
anc_planner.run_main() """

""" 
case 10)
anc_planner = main_testing_copy.AnchoragePlanner()
data = [(17900, 18400, 1000-utils.EXTRA_LENGTH), 
        (18100, 28000,750-utils.EXTRA_LENGTH), 
        (18300, 28200, 750-utils.EXTRA_LENGTH), 
        (28400, 28500, 500-utils.EXTRA_LENGTH)]
area = utils.areaMaxInscribedCircle(anc_planner.anchorage)
anc_planner.populate_time_list(data)
totals, _, _ = anc_planner.run_main()
for total in totals:
    print(total)
utilavg = utils.obtainAverageArea(totals, area, data_generator.UPPER_LIMIT, data_generator.LOWER_LIMIT, param='area')
remavg = utils.obtainAverageArea(totals, anc_planner.anchorage.area, data_generator.UPPER_LIMIT, data_generator.LOWER_LIMIT, param='util')
risk = (totals[-1]['ra'][0]/totals[-1]['ra'][1] + totals[-1]['rd'][0]/totals[-1]['rd'][1])/2
dist = totals[-1]['d'][0]/totals[-1]['d'][1]
time = totals[-1]['t'][0]/totals[-1]['t'][1]

print('risk (m) = ', risk, '\naverage distance travelled (m) = ', dist, '\naverage waiting time (mins) = ', time, '\naverage effective remaining area (%) = ', round(remavg * 100, 2), '\naverage utilisation rate (%) = ', round(utilavg * 100, 2)) """