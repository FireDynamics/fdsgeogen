import sys
from itertools import product
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

def get_val(node, name, opt=False):
    if name in node.attrib:
        return eval(node.attrib["nx"], {}, vars)
    elif (opt) and (name in vars):
        return vars[name]
    else:
        print "error reading attribute %s from node %s"%(name, node)
        sys.exit()

def write_to_fds(vars, text):
    if type(vars['fds_file']) != file:
        open_fds_file(vars)
        
    vars['fds_file'].write(text)

def close_fds_file(vars):
    write_to_fds(vars, "&TAIL/\n")
    vars['fds_file'].close()
    
def open_fds_file(vars):
    if type(vars['fds_file']) == file:
        close_fds_file(vars)
        
    vars['fds_file'] = open(vars['outfile'], 'w')
    write_to_fds(vars, "&HEAD CHID='%s', TITLE='%s' /\n"%(vars['chid'], vars['title']))


def info(node, vars):

    if 'chid' in node.attrib: 
        vars['chid'] = eval(node.attrib["chid"], {}, vars)
        print "chid: %s"%vars['chid']

    if 'outfile' in node.attrib: 
        vars['outfile'] = eval(node.attrib["outfile"], {}, vars)
        print "outfile: %s"%vars['outfile']
        open_fds_file(vars)
        
def obst(node, vars):
    geometry = "XB=%f,%f,%f,%f,%f,%f"%(eval(node.attrib["x1"], {}, vars),
                                       eval(node.attrib["x2"], {}, vars),
                                       eval(node.attrib["y1"], {}, vars),
                                       eval(node.attrib["y2"], {}, vars),
                                       eval(node.attrib["z1"], {}, vars),
                                       eval(node.attrib["z2"], {}, vars))
    color = ""
    if 'color' in node.attrib:
        color = "COLOR='%s'"%node.attrib["color"]
    write_to_fds(vars,"&OBST %s %s/\n"%(geometry, color))
    
def hole(node, vars):
    write_to_fds(vars,"&HOLE XB=%f,%f,%f,%f,%f,%f /\n"%(eval(node.attrib["x1"], {}, vars),
                                                        eval(node.attrib["x2"], {}, vars),
                                                        eval(node.attrib["y1"], {}, vars),
                                                        eval(node.attrib["y2"], {}, vars),
                                                        eval(node.attrib["z1"], {}, vars),
                                                        eval(node.attrib["z2"], {}, vars)))
                                                        
def mesh(node, vars):
    nmeshes = 1
    px = 1
    py = 1
    pz = 1
    if 'px' in node.attrib: 
        px = eval(node.attrib["px"], {}, vars)
    if 'py' in node.attrib: 
        py = eval(node.attrib["py"], {}, vars)
    if 'pz' in node.attrib: 
        pz = eval(node.attrib["pz"], {}, vars)                
    
    
    nmeshes = px * py * pz
    
    gnx = get_val(node, "nx", opt=True)
    gny = get_val(node, "ny", opt=True)
    gnz = get_val(node, "nz", opt=True)
    
    lnx = gnx / px
    lny = gny / py                
    lnz = gnz / pz

    gxmin = get_val(node, "xmin", opt=True)
    gxmax = get_val(node, "xmax", opt=True)    
    gymin = get_val(node, "ymin", opt=True)
    gymax = get_val(node, "ymax", opt=True)    
    gzmin = get_val(node, "zmin", opt=True)
    gzmax = get_val(node, "zmax", opt=True)    
        
    dx = (gxmax - gxmin) / px
    dy = (gymax - gymin) / py
    dz = (gzmax - gzmin) / pz        

    for ix in range(px):
        for iy in range(py):
            for iz in range(pz):            
                xmin = gxmin + ix*dx
                xmax = gxmin + (ix+1)*dx                
                ymin = gymin + iy*dy
                ymax = gymin + (iy+1)*dy                
                zmin = gzmin + iz*dz
                zmax = gzmin + (iz+1)*dz                
                
                write_to_fds(vars,"&MESH IJK=%d,%d,%d, XB=%f,%f,%f,%f,%f,%f /\n"%(
                             lnx, lny, lnz,
                             xmin, xmax, ymin, ymax, zmin, zmax))

def boundary(node, vars):
    if 'x' in node.attrib: 
        if node.attrib['x'] == "open":
            write_to_fds(vars, "&VENT MB='XMIN' ,SURF_ID='OPEN' /\n")
            write_to_fds(vars, "&VENT MB='XMAX' ,SURF_ID='OPEN' /\n")            

    if 'y' in node.attrib: 
        if node.attrib['x'] == "open":
            write_to_fds(vars, "&VENT MB='YMIN' ,SURF_ID='OPEN' /\n")
            write_to_fds(vars, "&VENT MB='YMAX' ,SURF_ID='OPEN' /\n")            

    if 'z' in node.attrib: 
        if node.attrib['z'] == "open":
            write_to_fds(vars, "&VENT MB='ZMIN' ,SURF_ID='OPEN' /\n")
            write_to_fds(vars, "&VENT MB='ZMAX' ,SURF_ID='OPEN' /\n")  
    if 'zmin' in node.attrib: 
        if node.attrib['zmin'] == "open":
            write_to_fds(vars, "&VENT MB='ZMIN' ,SURF_ID='OPEN' /\n")
    if 'zmax' in node.attrib: 
        if node.attrib['zmax'] == "open":
            write_to_fds(vars, "&VENT MB='ZMAX' ,SURF_ID='OPEN' /\n")  


def input(node, vars):
    if 'text' in node.attrib: 
        write_to_fds(vars,"&%s /\n"%(node.attrib["text"]))
    if 'str' in node.attrib: 
        write_to_fds(vars,"&%s /\n"%(eval(node.attrib["text"], {}, vars)))

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

def fire(node, vars):
    if node.attrib['type'] == "burningbox":
        cx = eval(node.attrib['cx'], {}, vars)
        cy = eval(node.attrib['cy'], {}, vars)        
        lz = eval(node.attrib['lz'], {}, vars)
        w2 = eval(node.attrib['width'], {}, vars) / 2.0                      
        h = eval(node.attrib['height'], {}, vars)                                
        box_obst  = "&OBST "
        box_obst += "XB=%f, %f, %f, %f, %f, %f"%(cx-w2, cx+w2, cy-w2, cy+w2, lz, lz+h)
        box_obst += "/\n"
        write_to_fds(vars, box_obst)
        
        write_to_fds(vars, "&REAC FUEL = 'METHANE' /\n")
        hrrpua = eval(node.attrib['hrr'], {}, vars) / (2.0*w2)**2
        write_to_fds(vars, "&SURF ID='burningbox', HRRPUA=%f /\n"%hrrpua)
        write_to_fds(vars, "&VENT XB=%f,%f,%f,%f,%f,%f SURF_ID='burningbox' color='RED'/\n"%(cx-w2, cx+w2, cy-w2, cy+w2, lz+h, lz+h))

def slice(node, vars):
    q = "QUANTITY='%s'"%node.attrib['q']
    v = ""
    if 'v' in node.attrib:
        if node.attrib['v'] == '1': v="VECTOR=.TRUE."
    if 'x' in node.attrib:
        pos = eval(node.attrib['x'], {}, vars)
        write_to_fds(vars, "&SLCF PBX=%e, %s %s /\n"%(pos, q, v))
    if 'y' in node.attrib:
        pos = eval(node.attrib['y'], {}, vars)
        write_to_fds(vars, "&SLCF PBY=%e, %s %s /\n"%(pos, q, v))
    if 'z' in node.attrib:
        pos = eval(node.attrib['z'], {}, vars)
        write_to_fds(vars, "&SLCF PBZ=%e, %s %s /\n"%(pos, q, v))
    
def paradim(node, dirlist):
    if 'name' in node.attrib:
        paralist = node.attrib['list'].split(',')
        np = len(paralist)
        if len(dirlist) == 0:
            for ip in paralist: dirlist.append({})

        if len(dirlist) != np: 
            print "wrong number of parameter!!"
            sys.exit()
        
        for ip in range(np):
            dirlist[ip][node.attrib['name']] = paralist[ip]
    
tree = ET.parse(str(sys.argv[1]))
root = tree.getroot()

params = {}

for node in root:
    if node.tag == 'para':
        if node.attrib['dim'] not in params:
            params[node.attrib['dim']] = []
        paradim(node, params[node.attrib['dim']])

for ipd in params:
    print "parameter dimension: %s"%ipd
    print params[ipd]

params_dim = len(params)

params_id = 0
for items in product(*[params[pd] for pd in params]):

    params_id += 1
    vars = {'outfile':"output.fds", 'chid':"chid", 'title':"title", 'fds_file_open':False, 'fds_file':0, 'params_id': params_id}
    for v in items:
        vars = dict(vars.items() + v.items())
    
    print vars 

    for node in root:
        #print node
    
        if node.tag == 'obst': obst(node, vars)
        if node.tag == 'hole': hole(node, vars)    
        if node.tag == 'var': var(node, vars)
        if node.tag == 'loop': loop(node, vars)
        if node.tag == 'info': info(node, vars)
        if node.tag == 'mesh': mesh(node, vars)
        if node.tag == 'input': input(node, vars)
    
        if node.tag == 'boundary': boundary(node, vars)
        if node.tag == 'fire': fire(node, vars)
        if node.tag == 'slice': slice(node, vars)

    close_fds_file(vars)
