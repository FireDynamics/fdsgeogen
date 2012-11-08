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

def div235(n):
    r = n
    while r%2 == 0 and r!= 0: r /= 2
    while r%3 == 0 and r!= 0: r /= 3
    while r%5 == 0 and r!= 0: r /= 5

    if r == 1: return True
    return False
