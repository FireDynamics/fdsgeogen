import numpy as np
import bisect

results = np.zeros([21, 4])
sprinklercolumns = range(1,6)
threshold = 68.0

for r in range(20):
	devc = np.loadtxt('id%03d/ffb_room_devc.csv'%r,delimiter=',', skiprows=2)

	print devc.shape

	timelist = []								# --Start-- Durchschnitt der Sprinklerausloesezeit
	for c in sprinklercolumns:
		if np.max(devc[:,c]) > threshold:
			timelist.append(devc[np.nonzero(devc[:,c]>threshold)[0][0],0])
		else:
			print "Sprinkler Nr. %d did not reach the threshold %.02f in Parametersample %02d."%(c,threshold,r)
	results[r,0] = np.average(timelist)					# --Ende-- Durchschnitt der Sprinklerausloesezeit

	s_means=[]									# --Start-- Durchschnitt der Schichthoehe in der 15. Minute
	for s in (8,12,16,20):
		mean = np.average(devc[-40:,s])
		s_means.append(mean)
	results[r,1] = np.average(s_means)					# --Ende-- Durchschnitt der Schichthoehe in der 15. Minute

	results[r,2] = np.average(devc[-1,23:27])-devc [1,23]		# Durchschnittliche Temperaturanstieg des Probekoerpers

	t_list =[]									# --Start-- Durchschnitt der Deckentemperatur nach 15. Minuten
	for t in (6,7,11,15,19):
		t_list.append(devc[-1,t])
	results[r,3] = np.average(t_list)					# --Ende-- Durchschnitt der Deckentemperatur nach 15. Minuten


print results
np.savetxt("results_run1.csv", results, delimiter=";", header="# Sprinklerausloesung [s]; Schichthoehe [m]; Temperaturanstieg [K]; Deckentemperatur [K]")
