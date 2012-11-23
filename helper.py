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
    r = n
    while r%2 == 0 and r!= 0: r /= 2
    while r%3 == 0 and r!= 0: r /= 3
    while r%5 == 0 and r!= 0: r /= 5

    if r == 1: return True
    return False
