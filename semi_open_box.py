import numpy as np

from helper import *

grid_spacing = 0.250
ID = ('semi_open_box_%.3f'%grid_spacing).replace('.','')

filename = ID + '.fds'
f = open(filename, 'w')

print "constructing fds file:       ", filename

nmeshes = 1
t_end = 500.0

length_box     = 10.0
length_domain  = 20.0
length_roof    = 12.0
length_opening =  1.0
wall_thickness =  1.0

HRR = 100

d = np.array([ -1, 1, -1, 1, 0, 1.5]) * length_domain / 2.0

grid = np.zeros(3)

grid  = (d[1::2] - d[::2]) / grid_spacing

while not div235(grid[0]): grid[0] += 1
while not div235(grid[1]): grid[1] += 1
while not div235(grid[2]): grid[2] += 1

print "computational domain [m]:    ", d
print "grid spacing [m]:            ", grid_spacing
print "grid size:                   ", grid

f.write("&HEAD CHID='%s', TITLE='Semi Open Box' /\n"%ID)
f.write("&TIME T_END=%e /\n"%t_end)

dnx = grid[0] / nmeshes
rnx = 0

if (grid[0] % nmeshes) != 0:
    dnx = grid[0] / (nmeshes-1)
    rnx = grid[0] % dnx
    
for m in range(nmeshes):
    nx = dnx
    if m == nmeshes-1 and rnx != 0: nx = rnx
    
    xmin = d[0] +  m*dnx       * grid_spacing 
    xmax = d[0] + (m*dnx + nx) * grid_spacing
    f.write("&MESH IJK=%d,%d,%d, XB=%e,%e,%e,%e,%e,%e /\n"%
                    (nx, grid[1], grid[2], 
                    xmin, xmax,
                    d[2], d[3],
                    d[4], d[5]) )
                

#####################################################################
# box boundaries        

# x min
p = length_box / 2.0
w = wall_thickness
obst(f, [-p-w, -p, -p-w, p+w, 0.0, 2*p], color="BLACK" ) 
# x max
obst(f, [p, p+w, -p-w, p+w, 0.0, 2*p], color="INVISIBLE" ) 

# y min
p = length_box / 2.0
w = wall_thickness
obst(f, [-p, p, -p-w, -p, 0.0, 2*p], color="INVISIBLE" ) 
# y max
obst(f, [-p-w, p+w, p, p+w, 0.0, 2*p], color="INVISIBLE" )

# roof
r = length_roof / 2.0
o = length_opening
obst(f, [-r, r, -r, r, 2*p+o, 2*p+o+w], color="BLACK" )

# add open boundaries
f.write("&VENT MB='XMIN' ,SURF_ID='OPEN' /\n")
f.write("&VENT MB='XMAX' ,SURF_ID='OPEN' /\n")
f.write("&VENT MB='YMIN' ,SURF_ID='OPEN' /\n")
f.write("&VENT MB='YMAX' ,SURF_ID='OPEN' /\n")
f.write("&VENT MB='ZMAX' ,SURF_ID='OPEN' /\n")

#####################################################################
# fire
p = length_box / 4.0
f.write("&REAC FUEL = 'METHANE' /\n")
f.write("&SURF ID='fire', HRRPUA=%d /\n"%HRR)
obst(f, [p-0.5, p+0.5, -0.5, +0.5, 0.0, 1.0], color="RED")
f.write("&VENT XB= %e, %e, %e, %e, %e, %e, SURF_ID='fire' /\n"%
        (p-0.5, p+0.5, -0.5, +0.5, 1.0, 1.0) )
                
f.write("&SLCF PBY=%e,  QUANTITY='TEMPERATURE', VECTOR=.TRUE. /\n"%(0.0))

#####################################################################
# devices

ndev = 20
for i in range(1,ndev+1):
    z = i * length_box/float(ndev)
    f.write("&DEVC ID='T1-%02d', XYZ=%e,%e,%e, QUANTITY='TEMPERATURE'  /\n"%(i, -length_box/4.0, 0.0, z))

ndev = 40
for i in range(1,ndev+1):
    x = i * length_domain/float(ndev) 
    f.write("&DEVC ID='T2-%02d', XYZ=%e,%e,%e, QUANTITY='U-VELOCITY'  /\n"%(i, -length_domain/2.0 + x, 0.0, length_box + 0.5*length_opening))

p = length_box / 2.0
f.write("&DEVC ID='T3-%02d', XB=%e,%e,%e,%e,%e,%e QUANTITY='MASS FLOW'  /\n"%(1, -p, +p, -p, -p, 2*p, 2*p+length_opening))
f.write("&DEVC ID='T3-%02d', XB=%e,%e,%e,%e,%e,%e QUANTITY='MASS FLOW'  /\n"%(2, -p, +p, +p, +p, 2*p, 2*p+length_opening))

f.write("&TAIL /\n")

f.close()
