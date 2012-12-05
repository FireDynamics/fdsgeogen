import numpy as np

from helper import *

grid_spacing = 0.100
ID = ('simple_station_%.3f'%grid_spacing).replace('.','')

filename = ID + '.fds'
f = open(filename, 'w')

print "constructing fds file:       ", filename

nmeshes = 8
grid_spacing = 0.10

t_end = 0.0

TTP  = 15
TTL  = 25 
TFP  = TTP + 7
TDW  = 2
TDN  = 4
TWW  = 0.2
THRR = 125

UB = 10
UL = 70
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

f.write("&HEAD CHID='%s', TITLE='Simple Metro Station Setup' /\n"%ID)
f.write("&TIME T_END=%e /\n"%t_end)

dnx = grid[0] / nmeshes
rnx = 0

if (grid[0] % nmeshes) != 0:
    dnx = grid[0] / (nmeshes-1)
    rnx = grid[0] % dnx
    
for m in range(nmeshes):
    nx = dnx
    if m == nmeshes-1 and rnx != 0: nx = rnx
    
    xmin = deff[0] +  m*dnx       * grid_spacing 
    xmax = deff[0] + (m*dnx + nx) * grid_spacing
    f.write("&MESH IJK=%d,%d,%d, XB=%e,%e,%e,%e,%e,%e /\n"%
                    (nx, grid[1], grid[2], 
                    xmin, xmax,
                    deff[2], deff[3],
                    deff[4], deff[5]) )
                

#####################################################################
# all boundary walls                
# x min
obst(f, [deff[0], d[0], deff[2], deff[3], deff[4], deff[5]], color="BLACK" ) 
# x max
obst(f, [d[1], deff[1], deff[2], deff[3], deff[4], deff[5]], color="BLACK" ) 

# y min
obst(f, [d[0], d[1], deff[2], d[2], deff[4], deff[5]], color="INVISIBLE" ) 
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
obst(f, [-OL/2., 0.0,  d[2], -UB/2.0, OHB, d[5]], color="ORANGE")
obst(f, [-OL/4., 0.0, -UB/2.0+BSB, UB/2.0-BSB, OHB, d[5]], color="ORANGE")
obst(f, [-OL/2., 0.0, UB/2.0, d[3], OHB, d[5]], color="ORANGE")

# tunnel hole
hole(f, [deff[0], 0, -GB/2., GB/2., d[4], UH])

# stair holes
hole(f, [d[0], d[0]+T1B, deff[2], d[2], OHB, d[5]])
hole(f, [deff[0], d[0], d[3], d[3]-T2B, OHB, d[5]])

#####################################################################
# train

# left
obst(f, [TTP, TTP+TTL, 0.0, -TWW, 0.0, UH-TWW], color="MIDNIGHT BLUE")
# right
obst(f, [TTP, TTP+TTL, -GB/2.0, -GB/2.0+TWW, 0.0, UH-TWW], color="BLUE")
# front
obst(f, [TTP+TTL-TWW, TTP+TTL, -GB/2.0, 0.0, 0.0, UH-TWW], color="MIDNIGHT BLUE")
# back
obst(f, [TTP-TWW, TTP, -GB/2.0, 0.0, 0.0, UH-TWW], color="MIDNIGHT BLUE")
# top
obst(f, [TTP, TTP+TTL, -GB/2.0, 0.0, OH-TWW, OH], color="POWDER BLUE")
# bottom
obst(f, [TTP, TTP+TTL, -GB/2.0, 0.0, d[4], 1.0], color="BLACK")


dist_door = TTL / (TDN+1)
for i in range(1,TDN+1):
    hole(f, [TTP + i*dist_door - TDW/2.0, TTP + i*dist_door + TDW/2.0, -GB/2.0, -GB/2.0+TWW, 1.0, UH-TWW])

#hole(f, [TTP+TWW, TTP+TTL-TWW, -GB/2.0+TWW, -TWW, 1.0, UH-TWW])

#####################################################################
# sources

# fire
f.write("&REAC FUEL = 'METHANE' /\n")
f.write("&SURF ID='fire', HRRPUA=%d /\n"%THRR)
obst(f, [TFP-0.5, TFP+0.5, -1.0-TWW, -TWW, 1.0, 1.5], color="RED")
f.write("&VENT XB= %e, %e, %e, %e, %e, %e, SURF_ID='fire' /\n"%
        (TFP-0.5, TFP+0.5, -1.0-TWW, -TWW, 1.5, 1.5) )
                
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
