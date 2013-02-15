import numpy as np
import re

def obst(f, domain, transp=False, color=None):
    f.write("&OBST XB=%e,%e,%e,%e,%e,%e"%
            (domain[0], domain[1],
            domain[2], domain[3],
            domain[4], domain[5]) )
    if transp:
        f.write(", COLOR='INVISIBLE'")
    
    if color != None:
        f.write(", COLOR='%s'"%color)

    f.write(" /\n")

def hole(f, domain):
    eps = 0.05
    f.write("&HOLE XB=%e,%e,%e,%e,%e,%e /\n"%
            (domain[0]-eps, domain[1]+eps,
            domain[2]-eps, domain[3]+eps,
            domain[4]-eps, domain[5]+eps) )

def div235(n):
    r = int(n)
    while r%2 == 0 and r!= 0: r /= 2
    while r%3 == 0 and r!= 0: r /= 3
    while r%5 == 0 and r!= 0: r /= 5

    if r == 1: return True
    return False

def devc(f, id, xr, yr, zr, quantity, spec_id=''):
    qnt_str = "QUANTITY='%s'"%quantity
    if spec_id != '': qnt_str += ", SPEC_ID='%s'"%spec_id
    i = 0
    
    if isinstance(xr, int) or isinstance(xr, float): xr = [xr]
    if isinstance(yr, int) or isinstance(yr, float): yr = [yr]
    if isinstance(zr, int) or isinstance(zr, float): zr = [zr]
    
    for x in xr:
        for y in yr:
            for z in zr:
                f.write("&DEVC ID='%s-%02d', XYZ=%e,%e,%e, %s /\n"%(id, i, x, y, z, qnt_str))
                i += 1

def translate(line, x, y, z):
#    print "================="
#    print line
    
    lcs=line.rstrip('/\n').split(',')
    
    first = -1
    for i in range(len(lcs)):

        first = lcs[i].find("XB=")

        if first != -1: 
#            print lcs[i:i+6] 
            fprefix = lcs[i].split('=')[0]
            fnumber = lcs[i].split('=')[1]
            fnumber = float(fnumber) + x
            
            lcs[i+0] = fprefix + "=" + str(fnumber)
            lcs[i+1] = str(float(lcs[i+1]) + x)
            lcs[i+2] = str(float(lcs[i+2]) + y)
            lcs[i+3] = str(float(lcs[i+3]) + y)
            lcs[i+4] = str(float(lcs[i+4]) + z)
            lcs[i+5] = str(float(lcs[i+5]) + z)

#            print lcs[i:i+6]
            
            new_line = ','.join(lcs) + " /\n"
#            print new_line
                        
            return new_line
            
    return line
    
