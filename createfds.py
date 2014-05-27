import sys
import ast
import numpy as np
from itertools import product
import xml.etree.ElementTree as ET


global_args = {}
global_args['reac'] = ['heat_of_combustion', 'soot_yield','C', 'H', 'fuel']
global_args['matl'] = ['specific_heat', 'conductivity', 'density', 'heat_of_combustion', 
                        'n_reactions', 'heat_of_reaction', 'nu_spec', 'reference_temperature',
                        'a', 'e', 'n_s', 'spec_id', 'emissivity', 'heating_rate', 'pyrolysis_range', 'matl_id', 'nu_matl']
global_args['surf'] = ['rgb', 'color', 'vel', 'hrrpua','heat_of_vaporization', 
                        'ignition_temperature', 'burn_away', 'matl_id', 'matl_mass_fraction', 
                        'thickness', 'external_flux', 'backing', 'hrrupa', 'stretch_factor', 'cell_size_factor']
global_args['obst'] = ['x1', 'x2', 'y1', 'y2', 'z1', 'z2', 'xb', 'surf_ids', 'surf_id', 'color']
global_args['hole'] = ['xb']
global_args['vent'] = ['xb', 'surf_id', 'color', 'dynamic_pressure']
global_args['slcf'] = ['pbx', 'pby', 'pbz', 'quantity', 'vector']

global_keys = {}
global_keys['reac']  = 'REAC'
global_keys['matl']  = 'MATL'
global_keys['surf']  = 'SURF'
global_keys['obst']  = 'OBST'
global_keys['hole']  = 'HOLE'
global_keys['vent']  = 'VENT'
global_keys['slcf']  = 'SLCF'

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

def add_var(key, value):
    global vars
    vars[key] = value
    
def del_var(key):
    global vars
    del vars[key]

def check_get_val(node, name, default):
    if check_val(node, name):
        return get_val(node, name)
    else:
        return default

def check_val(node, lst, req=False):
    if type(lst) is not list: 
        lst = [ lst ]
    for item in lst:
        if not item in node.attrib: 
            if req:
                print "required attribute %s not found in node %s"%(item, node)
                sys.exit()
            return False
    return True 

def get_val(node, name, opt=False):
    if name in node.attrib:
        return eval(node.attrib[name], {}, vars)
    elif (opt) and (name in vars):
        return vars[name]
    else:
        print "error reading attribute %s from node %s"%(name, node)
        sys.exit()

def write_to_fds(text):
    if type(vars['fds_file']) != file:
        open_fds_file()
        
    vars['fds_file'].write(text)

def close_fds_file():
    write_to_fds("&TAIL/\n")
    vars['fds_file'].close()
    
def open_fds_file():
    if type(vars['fds_file']) == file:
        close_fds_file()
        
    vars['fds_file'] = open(vars['outfile'], 'w')
    write_to_fds("&HEAD CHID='%s', TITLE='%s' /\n"%(vars['chid'], vars['title']))


def info(node):

    if check_val(node, ['chid','outfile'], req=True):
        vars['chid'] = get_val(node,"chid")
        vars['title'] = get_val(node,"title", opt=True)
        vars['outfile'] = get_val(node,"outfile")                
        print "chid    : %s"%vars['chid']
        print "title   : %s"%vars['title']        
        print "outfile : %s"%vars['outfile']
        open_fds_file()
        
def obst(node):
    line = "XB=%f,%f,%f,%f,%f,%f"%(eval(node.attrib["x1"], {}, vars),
                                       eval(node.attrib["x2"], {}, vars),
                                       eval(node.attrib["y1"], {}, vars),
                                       eval(node.attrib["y2"], {}, vars),
                                       eval(node.attrib["z1"], {}, vars),
                                       eval(node.attrib["z2"], {}, vars))
    
    if check_val(node, 'color'):
        line += " COLOR='%s'"%node.attrib["color"]
        
    if check_val(node, 'surf_id'):
        line += " SURF_ID='%s'"%node.attrib["surf_id"]

    comment=""
    if check_val(node, 'comment'):
        comment = node.attrib["comment"]

    write_to_fds("&OBST %s / %s\n"%(line, comment))
    
def hole(node):
    write_to_fds("&HOLE XB=%f,%f,%f,%f,%f,%f /\n"%(eval(node.attrib["x1"], {}, vars),
                                                        eval(node.attrib["x2"], {}, vars),
                                                        eval(node.attrib["y1"], {}, vars),
                                                        eval(node.attrib["y2"], {}, vars),
                                                        eval(node.attrib["z1"], {}, vars),
                                                        eval(node.attrib["z2"], {}, vars)))

def my_room(node):
    x1 = get_val(node, "x1", opt=True)
    x2 = get_val(node, "x2", opt=True)
    y1 = get_val(node, "y1", opt=True)
    y2 = get_val(node, "y2", opt=True)
    z1 = get_val(node, "z1", opt=True)
    z2 = get_val(node, "z2", opt=True)                    
      
    bx1 = check_get_val(node, "bx1", 0)
    bx2 = check_get_val(node, "bx2", 0)
    by1 = check_get_val(node, "by1", 0)
    by2 = check_get_val(node, "by2", 0)
    bz1 = check_get_val(node, "bz1", 0)
    bz2 = check_get_val(node, "bz2", 0)                    
    
    wt = check_get_val(node, "wt", 0.0)

    ax = check_get_val(node, "ax", 1)
    ay = check_get_val(node, "ay", 1)
    az = check_get_val(node, "az", 1)
    
    delta = get_val(node, "delta", opt=True)
    
    dxmin = x1 - bx1*wt  
    dxmax = x2 + bx2*wt      
    dymin = y1 - by1*wt  
    dymax = y2 + by2*wt      
    dzmin = z1 - bz1*wt  
    dzmax = z2 + bz2*wt      

    nx = int(div235((dxmax - dxmin) / delta))
    ny = int(div235((dymax - dymin) / delta))
    nz = int(div235((dzmax - dzmin) / delta))        
      
    if ax==1:
        dxmax = dxmin + nx*delta
    else:
        dxmin = dxmax - nx*delta

    if ay==1:
        dymax = dymin + ny*delta
    else:
        dymin = dymax - ny*delta

    if az==1:
        dzmax = dzmin + nz*delta
    else:
        dzmin = dzmax - nz*delta

    add_var("xmin", dxmin)
    add_var("xmax", dxmax)
    add_var("ymin", dymin)
    add_var("ymax", dymax)
    add_var("zmin", dzmin)
    add_var("zmax", dzmax)                    
               
    add_var("nx", nx)
    add_var("ny", ny)
    add_var("nz", nz)        
                                                        
def mesh(node):
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
                
                write_to_fds("&MESH IJK=%d,%d,%d, XB=%f,%f,%f,%f,%f,%f /\n"%(
                             lnx, lny, lnz,
                             xmin, xmax, ymin, ymax, zmin, zmax))

def boundary(node):
    if 'x' in node.attrib: 
        if node.attrib['x'] == "open":
            write_to_fds("&VENT MB='XMIN' ,SURF_ID='OPEN' /\n")
            write_to_fds("&VENT MB='XMAX' ,SURF_ID='OPEN' /\n")            

    if 'y' in node.attrib: 
        if node.attrib['x'] == "open":
            write_to_fds("&VENT MB='YMIN' ,SURF_ID='OPEN' /\n")
            write_to_fds("&VENT MB='YMAX' ,SURF_ID='OPEN' /\n")            

    if 'z' in node.attrib: 
        if node.attrib['z'] == "open":
            write_to_fds("&VENT MB='ZMIN' ,SURF_ID='OPEN' /\n")
            write_to_fds("&VENT MB='ZMAX' ,SURF_ID='OPEN' /\n")  
    if 'zmin' in node.attrib: 
        if node.attrib['zmin'] == "open":
            write_to_fds("&VENT MB='ZMIN' ,SURF_ID='OPEN' /\n")
    if 'zmax' in node.attrib: 
        if node.attrib['zmax'] == "open":
            write_to_fds("&VENT MB='ZMAX' ,SURF_ID='OPEN' /\n")  

def init(node):
    line = "TEMPERATURE=%f XB=%f,%f,%f,%f,%f,%f"%(eval(node.attrib["temperature"], {}, vars), 
									   eval(node.attrib["x1"], {}, vars),
                                       eval(node.attrib["x2"], {}, vars),
                                       eval(node.attrib["y1"], {}, vars),
                                       eval(node.attrib["y2"], {}, vars),
                                       eval(node.attrib["z1"], {}, vars),
                                       eval(node.attrib["z2"], {}, vars))
    comment=""
    if check_val(node, 'comment'):
        comment = node.attrib["comment"]
		
    write_to_fds("&INIT %s / %s \n"%(line, comment))   
	
def input(node):
    if check_val(node, 'text'):
        write_to_fds("&%s /\n"%(node.attrib["text"]))
    if check_val(node, 'str'):
        write_to_fds("&%s /\n"%(get_val(node,"str")))

def dump(node):
    if check_val(node, 'text'):
        write_to_fds("%s\n"%(node.attrib["text"]))
    if check_val(node, 'str'):
        write_to_fds("%s\n"%(get_val(node,"str")))
    if check_val(node, 'file'):
        f = open(node.attrib["file"], 'r')
        for line in f:
            write_to_fds("%s\n"%line.rstrip('\n'))
        f.close()

def var(node):
    global vars
    for att in node.attrib:
        vars[att] = eval(node.attrib[att], globals(), vars)
        #print "added variable: %s = %s"%(att, str(vars[att]))

def process_node(node):

    global vars
    line=''
    if check_val(node, 'id', req=False):
        line += "ID='%s'"%get_val(node, 'id') 
    else:
        line += "ID='none'"
    
    args = global_args[node.tag]

    for arg in args:
        if check_val(node, arg):

            vec_post=''
            if node.attrib[arg].find(';') != -1:
                vec_post = '(' + node.attrib[arg].split(';')[0] + ')'
                val = eval(node.attrib[arg].split(';')[1], globals(), vars)
            else:
                val = get_val(node, arg)
            if isinstance(val, tuple):
                line += ", %s%s="%(arg.upper(),vec_post)
                first = True
                for el in val:
                    if not first:
                        line += ", "
                    first = False
                    
                    if isinstance(el, basestring):
                        line += "'%s'"%(el)
                    else:
                        line += "%f"%(el)
            else:
                if isinstance(val, basestring):
                    line += ", %s='%s'"%(arg.upper(),val)
                else:
                    line += ", %s=%f"%(arg.upper(),val)
                
    all_args = args[:]
    all_args.extend(['id', 'comment'])

    for att in node.attrib:
        #print "checking attribute %s"%att
        if att not in all_args:
            print "WARNING: unknown argument %s"%att
    
    comment = ''
    if check_val(node, 'comment'):
        comment = node.attrib['comment']

    write_to_fds("&%s %s/ %s\n"%(global_keys[node.tag], line, comment))


def loop(node):

    # integer iteration from start to stop
    if 'start' in node.attrib and 'stop' in node.attrib:
        start = int(get_val(node,'start'))
        stop  = int(get_val(node,'stop'))
    
        for loop_i in range(start, stop):
            add_var(node.attrib['var'], loop_i)
            traverse(node)
            del_var(node.attrib['var'])
            
    if 'list' in node.attrib:
        llist = node.attrib['list'].split(',')
        for loop_i in llist:
            add_var(node.attrib['var'], loop_i.strip())
            traverse(node)
            del_var(node.attrib['var'])

def fire(node):
    if node.attrib['type'] == "burningbox":
        cx = eval(node.attrib['cx'], {}, vars)
        cy = eval(node.attrib['cy'], {}, vars)        
        lz = eval(node.attrib['lz'], {}, vars)
        w2 = eval(node.attrib['width'], {}, vars) / 2.0                      
        h = eval(node.attrib['height'], {}, vars)                                
        box_obst  = "&OBST "
        box_obst += "XB=%f, %f, %f, %f, %f, %f"%(cx-w2, cx+w2, cy-w2, cy+w2, lz, lz+h)
        box_obst += "/\n"
        write_to_fds(box_obst)
        
        write_to_fds("&REAC FUEL = 'METHANE' /\n")
        hrrpua = eval(node.attrib['hrr'], {}, vars) / (2.0*w2)**2
        write_to_fds("&SURF ID='burningbox', HRRPUA=%f /\n"%hrrpua)
        write_to_fds("&VENT XB=%f,%f,%f,%f,%f,%f SURF_ID='burningbox' color='RED'/\n"%(cx-w2, cx+w2, cy-w2, cy+w2, lz+h, lz+h))

def slice(node):
    q = "QUANTITY='%s'"%node.attrib['q']
    v = ""
    if 'v' in node.attrib:
        if node.attrib['v'] == '1': v="VECTOR=.TRUE."
    if 'x' in node.attrib:
        pos = eval(node.attrib['x'], {}, vars)
        write_to_fds("&SLCF PBX=%e, %s %s /\n"%(pos, q, v))
    if 'y' in node.attrib:
        pos = eval(node.attrib['y'], {}, vars)
        write_to_fds("&SLCF PBY=%e, %s %s /\n"%(pos, q, v))
    if 'z' in node.attrib:
        pos = eval(node.attrib['z'], {}, vars)
        write_to_fds("&SLCF PBZ=%e, %s %s /\n"%(pos, q, v))
    
def paradim(node, dirlist):
    check_val(node, ["var"], req=True)

    if check_val(node, ["list"]):
        #paralist = ast.literal_eval(node.attrib['list'])
        paralist = eval(node.attrib['list'])
        
    if check_val(node, ["file"]):
        col=0
        if check_val(node, ["col"]):
            col = int(get_val(node, "col"))
        paralist = np.loadtxt(node.attrib["file"], usecols=(col,), delimiter=',')
        
    nump = len(paralist)
    if len(dirlist) == 0:
        for ip in paralist: dirlist.append({})

    if len(dirlist) != nump: 
        print "wrong number of parameter!!"
        sys.exit()
    
    for ip in range(nump):
        dirlist[ip][node.attrib['var']] = paralist[ip]

def section(node):
    traverse(node)

def traverse(root):
    for node in root:
        if node.tag in global_keys:
            process_node(node)
        else:
            globals()[node.tag](node)
 
def dbg(node):
    print get_val(node, "print")

def device(node):
    check_val(node, ["q" ,"id"], req=True)
    q = get_val(node, "q", opt=True)
    id = get_val(node, "id", opt=True)
    if check_val(node, ["x1", "x2", "y1", "y2", "z1", "z2"]):
        x1 = get_val(node, "x1", opt=True)
        x2 = get_val(node, "x2", opt=True)
        y1 = get_val(node, "y1", opt=True)
        y2 = get_val(node, "y2", opt=True)
        z1 = get_val(node, "z1", opt=True)
        z2 = get_val(node, "z2", opt=True)
        write_to_fds("&DEVC ID='%s' XB=%f,%f,%f,%f,%f,%f QUANTITY='%s'/\n"%(id,x1,x2,y1,y2,z1,z2,q))
        return True
    if check_val(node, ["x", "y", "z"]):
        x = get_val(node, "x", opt=True)
        y = get_val(node, "y", opt=True)
        z = get_val(node, "z", opt=True)
        write_to_fds("&DEVC ID='%s' XYZ=%f,%f,%f QUANTITY='%s'/\n"%(id,x,y,z,q))
        return True
    return False

def para(node):
    pass

#################### MAIN LOOP
tree = ET.parse(str(sys.argv[1]))
root = tree.getroot()

params = {}
vars = {}

for node in root:
    if node.tag == 'para':
        if node.attrib['dim'] not in params:
            params[node.attrib['dim']] = []
        paradim(node, params[node.attrib['dim']])

para_id = 0
for items in product(*[params[pd] for pd in params]):

    vars = {'outfile':"output.fds", 'chid':"chid", 'title':"title", 'fds_file_open':False, 'fds_file':0, 'para_id': para_id}
    para_id += 1
    
    for v in items:
        vars = dict(vars.items() + v.items())
        print v
    
    traverse(root)

    close_fds_file()
