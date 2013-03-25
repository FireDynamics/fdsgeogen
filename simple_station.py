import numpy as np

from helper import *

grid_spacing = 0.100
nmeshes = 16
ID = ('simple_station_g%.3f_n%03d'%(grid_spacing, nmeshes)).replace('.','')

filename = ID + '.fds'
f = open(filename, 'w')

print "constructing fds file:       ", filename


t_end = 0.0

TTP  = 15
TTL  = 25 
TFP  = TTP + 7
TDW  = 2
TDN  = 4
TWW  = 0.2
THRR = 10000

UB = 11.2
UL = 80.0
UH =  3.2
BSB = 3.2
TU = 9.6
UGH = 0.8

GB = UB - 2*BSB

TL = 5.6

OB = 16.0
OL = 16.0
OH =  3.2
OHB = 5.6

T1B = 8.0
T2B = 8.0

minb = 0.8

d = np.array([ 
            -(OL), (UL + TL),
            -(OB/2.0), (OB/2.0)+T1B,
             0.0, (OH + OHB) 
             ])

deff = d + minb*np.array([-1, 1, -1, 1, 0, 1])

grid = np.zeros(3)

grid  = (deff[1::2] - deff[::2]) / grid_spacing + np.array([1,1,1])
grid = grid.astype(int)

while not (div235(grid[0]) and grid[0]%nmeshes==0): grid[0] += 1
while not div235(grid[1]): grid[1] += 1
while not div235(grid[2]): grid[2] += 1

print "computational domain [m]:    ", d

b = (grid_spacing * grid - (deff[1::2] - deff[::2]))
deff[1]  += b[0]
deff[3]  += b[1]
deff[5]  += b[2]

print "adding boundary buffer [m]:  ", b
print "corrected domain [m]:        ", deff
print "grid spacing [m]:            ", grid_spacing
print "grid size:                   ", grid

f.write("&HEAD CHID='%s', TITLE='Simple Metro Station Setup' /\n"%ID)
f.write("&TIME T_END=%e /\n"%t_end)
f.write("&PRES MAX_PRESSURE_ITERATIONS=1000 /\n")

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
obst(f, [deff[0], d[0], deff[2], deff[3], deff[4], deff[5]], color="INVISIBLE" ) 
# x max
obst(f, [d[1], deff[1], deff[2], deff[3], deff[4], deff[5]], color="INVISIBLE" ) 

# y min
obst(f, [d[0], d[1], deff[2], d[2], deff[4], deff[5]], color="INVISIBLE" ) 
# y max
obst(f, [d[0], d[1], d[3], deff[3], deff[4], deff[5]], color="INVISIBLE" ) 

# z min
#obst(f, [d[0], d[1], d[2], d[3], deff[4], d[4]], color="GRAY" ) 
# z max
obst(f, [d[0], d[1], d[2], d[3], d[5], deff[5]], color="INVISIBLE" ) 


# add open boundaries
f.write("&VENT MB='XMIN' ,SURF_ID='OPEN' /\n")
f.write("&VENT MB='XMAX' ,SURF_ID='OPEN' /\n")
f.write("&VENT MB='YMIN' ,SURF_ID='OPEN' /\n")
f.write("&VENT MB='YMAX' ,SURF_ID='OPEN' /\n")

#####################################################################
# platforms
obst(f, [0.0, UL, -UB/2.0, -UB/2.0 + BSB, 0.0, UGH], color="BRICK" ) 
obst(f, [0.0, UL,  UB/2.0 - BSB, UB/2.0, 0.0, UGH], color="BRICK" ) 

#####################################################################
# lower room walls
# y walls
obst(f, [0.0, UL, d[2], -UB/2.0, d[4], d[5]], color="INVISIBLE")
obst(f, [0.0, UL,  UB/2.0, d[3], d[4], d[5]], color="ORANGE")

# top wall
obst(f, [TU, d[1], -UB/2.0, UB/2.0, UH+UGH, d[5]], color="INVISIBLE")
# top wall between stairs
obst(f, [0.0, TU, -UB/2.0+BSB, UB/2.0-BSB, UH+UGH, d[5]], color="ORANGE")

# back wall
obst(f, [UL, d[1], d[2], d[3], d[4], d[5]], color="ORANGE")
# tunnel hole
hole(f, [UL, deff[1], -GB/2., GB/2., d[4], UH+UGH])

#####################################################################
# upper room

# floor above tunnel
obst(f, [d[0], 0.0, d[2], d[3], d[4], OHB], color="BRICK")

# walls
obst(f, [-OL/2., 0.0,  d[2], -UB/2.0, OHB, d[5]], color="INVISIBLE")
obst(f, [-OL/4., 0.0, -UB/2.0+BSB, UB/2.0-BSB, OHB, d[5]], color="ORANGE")
obst(f, [-OL/2., 0.0, UB/2.0, d[3], OHB, d[5]], color="ORANGE")

# tunnel hole
hole(f, [deff[0], 0, -GB/2., GB/2., d[4], UH+UGH])

# level connecting stairs
nsteps = int((OH+OHB -UH-UGH) / grid_spacing)
slope  = float(OH) / float(TU)
dz     = float(OH+OHB -UH-UGH) / nsteps
for i in range(nsteps):
    # top
    xmin = TU * i / float(nsteps)
    xmax = TU
    zmax = d[5] - i * dz
    zmin = d[5] - (i+1) * dz
    
    wzmax = zmin + dz
    
    obst(f, [xmin, xmax, -UB/2.0, -UB/2.0+BSB, zmin, zmax], color="MELON")
    obst(f, [xmin, xmax, UB/2.0-BSB, UB/2.0, zmin, zmax], color="MELON")
    # bottom
    xmin = 0.0
    xmax = TU * i / float(nsteps-1)
    zmax = OHB - i * dz
    zmin = OHB - (i+1) * dz
    wzmin = zmax
    wxmin = TU * (i-1) / float(nsteps-1)
    if i == 0: wxmin = 0.0
    wxmax = xmax
    obst(f, [xmin, xmax, -UB/2.0, -UB/2.0+BSB, zmin, zmax], color="CHOCOLATE")
    obst(f, [xmin, xmax, UB/2.0-BSB, UB/2.0, zmin, zmax], color="CHOCOLATE")
    # wall
    obst(f, [wxmin, wxmax, UB/2.0-BSB, UB/2.0-BSB+0.8, wzmin, wzmax], color="MELON")
    obst(f, [wxmin, wxmax, -UB/2.0+BSB, -UB/2.0+BSB-0.8, wzmin, wzmax], color="MELON")


# stair holes
hole(f, [d[0], d[0]+T1B, deff[2], d[2], OHB, d[5]])
hole(f, [deff[0], d[0], d[3]-T2B, d[3], OHB, d[5]])

#####################################################################
# train

# left
#obst(f, [TTP, TTP+TTL, 0.0, -TWW, 0.0, UH+UGH-TWW], color="MIDNIGHT BLUE")
# right
#obst(f, [TTP, TTP+TTL, -GB/2.0, -GB/2.0+TWW, 0.0, UH+UGH-TWW], color="BLUE")
# front
#obst(f, [TTP+TTL-TWW, TTP+TTL, -GB/2.0, 0.0, 0.0, UH+UGH-TWW], color="MIDNIGHT BLUE")
# back
#obst(f, [TTP-TWW, TTP, -GB/2.0, 0.0, 0.0, UH+UGH-TWW], color="MIDNIGHT BLUE")
# top
#obst(f, [TTP-TWW, TTP+TTL, -GB/2.0, 0.0, UH+UGH-TWW, UH+UGH], color="POWDER BLUE")
# bottom
#obst(f, [TTP, TTP+TTL, -GB/2.0, 0.0, d[4], UGH], color="BLACK")


#dist_door = TTL / (TDN+1)
#for i in range(1,TDN+1):
#    hole(f, [TTP + i*dist_door - TDW/2.0, TTP + i*dist_door + TDW/2.0, -GB/2.0, -GB/2.0+TWW, UGH, UH+UGH-TWW-0.5])

#hole(f, [TTP+TWW, TTP+TTL-TWW, -GB/2.0+TWW, -TWW, 1.0, UH-TWW])


tf = open("input_train.fds", "r")

for line in tf:
    f.write(translate(line, 20, 1.0, UGH))

tf.close()


#####################################################################
# sources

# fire
#f.write("&REAC FUEL = 'METHANE' /\n")
#f.write("&SURF ID='fire', HRRPUA=%d /\n"%THRR)
#obst(f, [TFP-0.5, TFP+0.5, -1.0-TWW, -TWW, 1.0, 1.5], color="RED")
#f.write("&VENT XB= %e, %e, %e, %e, %e, %e, SURF_ID='fire' /\n"%
#        (TFP-0.5, TFP+0.5, -1.0-TWW, -TWW, 1.5, 1.5) )
                
#vents
#f.write("&SURF ID='inlet', VEL=-10.0 /\n")
#f.write("&VENT XB=%e, %e, %e, %e, %e, %e, SURF_ID='inlet' /\n"%(UL+TL, UL+TL, -GB/2.0, GB/2.0, d[4], UH))

#### output

## lower room
f.write("&SLCF PBZ=%e,  QUANTITY='TEMPERATURE', VECTOR=.TRUE. /\n"%(UGH+2.4))
f.write("&SLCF PBY=%e,  QUANTITY='TEMPERATURE', VECTOR=.TRUE. /\n"%( GB/2.0 + 1.6))
f.write("&SLCF PBY=%e,  QUANTITY='TEMPERATURE', VECTOR=.TRUE. /\n"%(-GB/2.0 - 1.6))
f.write("&SLCF PBY=0.0, QUANTITY='TEMPERATURE', VECTOR=.TRUE. /\n")

## upper room
f.write("&SLCF PBX=%e, QUANTITY='TEMPERATURE', VECTOR=.TRUE. /\n"%(d[0]+T1B/2.4))
f.write("&SLCF PBY=%e, QUANTITY='TEMPERATURE', VECTOR=.TRUE. /\n"%(d[3]-T2B/2.4))
f.write("&SLCF PBZ=%e,  QUANTITY='TEMPERATURE', VECTOR=.TRUE. /\n"%(OHB+2.4))


f.write("&SLCF PBZ=%e,  QUANTITY='TEMPERATURE', VECTOR=.TRUE. /\n"%(UGH+2.4))

# devices

ndev = 10
b    = 0.2
devc(f, "T1", 10.0, -GB/2.0 - 1.6, np.linspace(UGH + b, UGH + UH - b, ndev), "TEMPERATURE")
devc(f, "S1", 10.0, -GB/2.0 - 1.6, np.linspace(UGH + b, UGH + UH - b, ndev), "MASS FRACTION", spec_id="SOOT")
devc(f, "T2", 10.0,  GB/2.0 + 1.6, np.linspace(UGH + b, UGH + UH - b, ndev), "TEMPERATURE")
devc(f, "S2", 10.0,  GB/2.0 + 1.6, np.linspace(UGH + b, UGH + UH - b, ndev), "MASS FRACTION", spec_id="SOOT")
devc(f, "T3", d[0]+T1B/2.0, d[2]+2.4, np.linspace(OHB + b, OHB + OH - b, ndev), "TEMPERATURE")
devc(f, "S3", d[0]+T1B/2.0, d[2]+2.4, np.linspace(OHB + b, OHB + OH - b, ndev), "MASS FRACTION", spec_id="SOOT")
devc(f, "T4", d[0]+2.4, d[3]-T2B/2, np.linspace(OHB + b, OHB + OH - b, ndev), "TEMPERATURE")
devc(f, "S4", d[0]+2.4, d[3]-T2B/2, np.linspace(OHB + b, OHB + OH - b, ndev), "MASS FRACTION", spec_id="SOOT")

ndev = 30
b    = 0.2
devc(f, "T5", np.linspace(+b, UL-b, ndev), -GB/2.0 - 1.6, UGH + 2.4, "TEMPERATURE")
devc(f, "S5", np.linspace(+b, UL-b, ndev), -GB/2.0 - 1.6, UGH + 2.4, "MASS FRACTION", spec_id="SOOT")

ndev = 10
b    = 0.2
devc(f, "T6", np.linspace(-OL+b, -b, ndev), -GB/2.0 - 1.6, OHB + 2.4, "TEMPERATURE")
devc(f, "S6", np.linspace(-OL+b, -b, ndev), -GB/2.0 - 1.6, OHB + 2.4, "MASS FRACTION", spec_id="SOOT")

f.write("&DEVC ID='Soot Density Upper Level', QUANTITY='DENSITY', SPEC_ID='SOOT', STATISTICS='VOLUME MEAN', XB=%e,%e,%e,%e,%e,%e /\n"%(d[0], 0.0, d[2], d[3], OHB, OHB+OH))
f.write("&DEVC XB= %e,%e,%e,%e,%e,%e, QUANTITY='MASS FLOW', ID='flow T1' /\n"%(d[0], d[0]+T1B, d[2], d[2], OHB, d[5]))
f.write("&DEVC XB= %e,%e,%e,%e,%e,%e, QUANTITY='MASS FLOW', ID='flow T2' /\n"%(d[0], d[0], d[3]-T2B, d[3], OHB, d[5]))
f.write("&DEVC XB= %e,%e,%e,%e,%e,%e, QUANTITY='MASS FLOW', ID='flow tunnel xmin' /\n"%(d[0], d[0], -GB/2., GB/2., d[4], UH+UGH))
f.write("&DEVC XB= %e,%e,%e,%e,%e,%e, QUANTITY='MASS FLOW', ID='flow tunnel xmax' /\n"%(d[1], d[1], -GB/2., GB/2., d[4], UH+UGH))


f.write("&TAIL /\n")

f.close()

