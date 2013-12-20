import sys
import numpy as np

data = np.loadtxt(sys.argv[1], skiprows=1)    

t_exp = data[:,1]
t_sim = data[:,2]
trust = data[:,3]

print np.sum(((t_sim - t_exp)/t_exp)**2) # + np.sum((1-trust)*1e6)








