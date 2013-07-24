import sys
import xml.etree.ElementTree as ET

def div235(n):
    r_init = int(n)
    while True:
        r = r_init
        while r%2 == 0 and r!= 0: r /= 2
        while r%3 == 0 and r!= 0: r /= 3
        while r%5 == 0 and r!= 0: r /= 5

        if r == 1: break
        r_init += 1
    return r_init

def obst(node, vars):
    print "OBST XB=%f,%f,%f,%f,%f,%f"%(eval(node.attrib["x1"], {}, vars),
                                       eval(node.attrib["x2"], {}, vars),
                                       eval(node.attrib["y1"], {}, vars),
                                       eval(node.attrib["y2"], {}, vars),
                                       eval(node.attrib["z1"], {}, vars),
                                       eval(node.attrib["z2"], {}, vars))

def var(node, vars):
    for att in node.attrib:
        vars[att] = eval(node.attrib[att], globals(), vars)
        print "added variable: %s = %f"%(att, vars[att])

def loop(node, vars):
    start = int(node.attrib['start'])
    stop  = int(node.attrib['stop'])
    
    for loop_i in range(start, stop):
        local_vars = dict(vars.items() + {node.attrib['var'] : loop_i}.items())
    
        for local_node in node:
            if local_node.tag == 'obst': obst(local_node, local_vars)
            if local_node.tag == 'var': var(local_node, local_vars)
            if local_node.tag == 'loop': loop(local_node, local_vars)

tree = ET.parse(str(sys.argv[1]))
root = tree.getroot()

vars = {}

for node in root:
    #print node
    
    if node.tag == 'obst': obst(node, vars)
    if node.tag == 'var': var(node, vars)
    if node.tag == 'loop': loop(node, vars)
