import sys
import numpy as np

row = int(sys.argv[2])
f_template = open(sys.argv[3],"r")

flux = np.loadtxt(sys.argv[1])[row,0]

for line in f_template:
    line = line.replace("#RAD_FLUX#", "%f"%flux)    
    print line.rstrip('\n')
    
f_template.close()
