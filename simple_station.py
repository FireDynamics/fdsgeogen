import numpy as np

from helper import *

filename = 'station.fds'
f = open(filename, 'w')

print "constructing fds file:       ", filename

grid_spacing = 0.25

t_end = 0.0

FP  = 3
HRR = 125

UB = 10
UL = 30
UH =  3
BSB = 3
TU = 2

GB = UB - 2*BSB

TL = 5

OB = 17
OL = 17
OH =  3
OHB = 4

T1B = 8.5
T2B = 8.5

minb = 0.5

d = np.array([ 
            -(OL), (UL + TL),
            -(OB/2.0), (OB/2.0),
             0.0, (OH + OHB) 
             ])

deff = d + minb*np.array([-1, 1, -1, 1, -1, 1])

grid = np.zeros(3)

grid  = (deff[1::2] - deff[::2]) / grid_spacing

while not div235(grid[0]): grid[0] += 1
while not div235(grid[1]): grid[1] += 1
while not div235(grid[2]): grid[2] += 1

print "computational domain [m]:    ", d

b = (grid_spacing * grid - (d[1::2] - d[::2])) * 0.5
deff[::2]  -= b 
deff[1::2] += b

print "adding boundary buffer [m]:  ", b
print "corrected domain [m]:        ", deff
print "grid spacing [m]:            ", grid_spacing
print "grid size:                   ", grid

f.write("&HEAD CHID='station', TITLE='Simple Metro Station Setup' /\n")
f.write("&TIME T_END=%e /\n"%t_end)

f.write("&MESH IJK=%d,%d,%d, XB=%e,%e,%e,%e,%e,%e /\n"%
                (grid[0], grid[1], grid[2], 
                deff[0], deff[1],
                deff[2], deff[3],
                deff[4], deff[5]) )
                

#####################################################################
# all boundary walls                
# x min
obst(f, [deff[0], d[0], deff[2], deff[3], deff[4], deff[5]], color="BLACK" ) 
# x max
obst(f, [d[1], deff[1], deff[2], deff[3], deff[4], deff[5]], color="BLACK" ) 

# y min
obst(f, [d[0], d[1], deff[2], d[2], deff[4], deff[5]], color="BLACK" ) 
# y max
obst(f, [d[0], d[1], d[3], deff[3], deff[4], deff[5]], color="BLACK" ) 

# z min
obst(f, [d[0], d[1], d[2], d[3], deff[4], d[4]], color="BLACK" ) 
# z max
obst(f, [d[0], d[1], d[2], d[3], d[5], deff[5]], color="INVISIBLE" ) 

#obst(f, [d[0], d[1], d[2], d[3], d[5] - b[2], d[5]], transp=True ) 

#####################################################################
# platforms
obst(f, [0.0, UL, -UB/2.0, -UB/2.0 + BSB, 0.0, 1.0], color="BRICK" ) 
obst(f, [0.0, UL,  UB/2.0 - BSB, UB/2.0, 0.0, 1.0], color="BRICK" ) 

#####################################################################
# lower room walls
# y walls
obst(f, [0.0, UL, d[2], -UB/2.0, d[4], d[5]], color="INVISIBLE")
obst(f, [0.0, UL,  UB/2.0, d[3], d[4], d[5]], color="ORANGE")

# top wall
obst(f, [TU, d[1], -UB/2.0, UB/2.0, UH, d[5]], color="INVISIBLE")
# top wall between stairs
obst(f, [0.0, TU, -UB/2.0+BSB, UB/2.0-BSB, UH, d[5]], color="ORANGE")

# back wall
obst(f, [UL, d[1], d[2], d[3], d[4], d[5]], color="ORANGE")
# tunnel hole
hole(f, [UL, deff[1], -GB/2., GB/2., d[4], UH])

#####################################################################
# upper room

# floor above tunnel
obst(f, [d[0], 0.0, d[2], d[3], d[4], OHB], color="BRICK")

# walls
obst(f, [-OL/2., 0.0,  d[2], -UB/2.0, UH, d[5]], color="ORANGE")
obst(f, [-OL/4., 0.0, -UB/2.0+BSB, UB/2.0-BSB, UH, d[5]], color="ORANGE")
obst(f, [-OL/2., 0.0, UB/2.0, d[3], UH, d[5]], color="ORANGE")

# tunnel hole
hole(f, [deff[0], 0, -GB/2., GB/2., d[4], UH])

# stair holes
hole(f, [d[0], d[0]+T1B, deff[2], d[2], OHB, d[5]])
hole(f, [deff[0], d[0], d[3], d[3]-T2B, OHB, d[5]])

#####################################################################
# train

#obst(f, [

#####################################################################
# sources

# fire
f.write("&REAC FUEL = 'METHANE' /\n")
f.write("&SURF ID='fire', HRRPUA=%d /\n"%HRR)
f.write("&VENT XB= %e, %e, %e, %e, %e, %e, SURF_ID='fire' /\n"%
        (FP-0.5, FP+0.5, 0.0, 1.0, 0.0, 0.0) )
                
#vents
#f.write("&SURF ID='inlet', VEL=-10.0 /\n")
#f.write("&VENT XB=%e, %e, %e, %e, %e, %e, SURF_ID='inlet' /\n"%(UL+TL, UL+TL, -GB/2.0, GB/2.0, d[4], UH))

# output
f.write("&SLCF PBY=0.0, QUANTITY='TEMPERATURE' /\n")
f.write("&SLCF PBY=0.0, QUANTITY='VELOCITY' /\n")

f.write("&SLCF PBZ=%e, QUANTITY='VELOCITY' /\n"%(UH-grid_spacing))
f.write("&SLCF PBZ=%e, QUANTITY='VELOCITY' /\n"%(OHB+OH))
f.write("&SLCF PBX=%e, QUANTITY='VELOCITY' /\n"%(TU/2.0))

f.write("&TAIL /\n")

f.close()
