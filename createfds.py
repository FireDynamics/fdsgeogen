import sys
import ast
import numpy as np
from itertools import product
import xml.etree.ElementTree as ET

#########################
##### FDS arguments #####
#########################
global_args = {}
global_args['reac'] = ['heat_of_combustion', 'soot_yield','C', 'H', 'fuel']
global_args['matl'] = ['specific_heat', 'conductivity', 'density', 'heat_of_combustion',
                       'n_reactions', 'heat_of_reaction', 'nu_spec', 'reference_temperature',
                       'a', 'e', 'n_s', 'spec_id', 'emissivity', 'heating_rate', 'pyrolysis_range', 'matl_id', 'nu_matl']
global_args['surf'] = ['rgb', 'color', 'vel', 'hrrpua','heat_of_vaporization',
                       'ignition_temperature', 'burn_away', 'matl_id', 'matl_mass_fraction',
                       'thickness', 'external_flux', 'backing', 'hrrupa', 'stretch_factor', 'cell_size_factor']
global_args['obst'] = ['x1', 'x2', 'y1', 'y2', 'z1', 'z2', 'xb', 'surf_ids', 'surf_id', 'color', 'bulk_density']
global_args['hole'] = ['xb', 'color']
global_args['vent'] = ['xb', 'surf_id', 'color', 'dynamic_pressure', 'tmp_exterior', 'mb', 'transparency']
global_args['slcf'] = ['pbx', 'pby', 'pbz', 'quantity', 'vector']

#########################
##### FDS key words #####
#########################
global_keys = {}
global_keys['reac']  = 'REAC'
global_keys['matl']  = 'MATL'
global_keys['surf']  = 'SURF'
global_keys['obst']  = 'OBST'
global_keys['hole']  = 'HOLE'
global_keys['vent']  = 'VENT'
global_keys['slcf']  = 'SLCF'

# accepted deviation when dealing with float arithmetic
epsilon = 0.0001

def div235(n):
    # DESCRIPTION:
    #  increases a given integer value until its factors only consist of 2, 3 and 5
    # INPUT:
    #  n        - integer value to increase (required)
    r_init = int(n)
    while True:
        r = r_init
        while r%2 == 0 and r!= 0: r /= 2
        while r%3 == 0 and r!= 0: r /= 3
        while r%5 == 0 and r!= 0: r /= 5

        if r == 1: break
        r_init += 1
    return r_init
    # end div235

###############################
##### VARIABLE MANAGEMENT #####
###############################
def add_var(key, value):
    # DESCRIPTION:
    #  adds a new variable
    # INPUT:
    #  key      - name of the new variable (required)
    #  value    - value assigned to the new variable (required)
    global vars
    vars[key] = value
    # end add_var

def del_var(key):
    # DESCRIPTION:
    #  deletes a variable
    # INPUT:
    #  key      - name of the variable to delete (required)
    global vars
    del vars[key]
    # end del_var

###########################
##### NODE EVALUATION #####
###########################
def check_get_val(node, name, default):
    # DESCRIPTION:
    #  checks via check_val if name is an attribute of node
    #  returns the value of name via get_val if possible, returns the specified default value otherwise
    # INPUT:
    #  node     - current node (required)
    #  name     - name of the attribute to return the value for (required)
    #  default  - value that should be returned if no value for name can be determined (required)
    if check_val(node, name):
        return get_val(node, name)
    else:
        return default
    # end check_get_val

def check_val(node, lst, opt=True):
    # DESCRIPTION:
    #  checks whether the items in lst are attributes of node and exits the program with an error message to
    #  standard output if a required attribute cannot be found
    # INPUT:
    #  node     - current node (required)
    #  lst      - list of attributes to search for (required)
    #  opt      - determines if the program should be exited if an attribute cannot be found (default: True)
    if type(lst) is not list:
        lst = [ lst ]
    for item in lst:
        if not item in node.attrib:
            if not opt:
                print "required attribute %s not found in node %s"%(item, node)
                sys.exit()
            return False
    return True
    # end check_val

def get_val(node, name, opt=False):
    # DESCRIPTION:
    #  gets value of an named attribute of node if possible,
    #  if no value for the attribute can be retrieved but the attribute appears in vars and is marked as optional
    #  the value from vars will be returned otherwise the program exits with an error message to standard output
    # INPUT:
    #  node     - current node (required)
    #  name     - name of the attribute to return the value for (required)
    #  opt      - determines if the program should be exited if no value for name can be found (default: False)
    if name in node.attrib:
        return eval(node.attrib[name], {}, vars)
    elif (opt) and (name in vars):
        return vars[name]
    else:
        print "error reading attribute %s from node %s"%(name, node)
        sys.exit()
    # end get_val

###############################
##### FDS FILE MANAGEMENT #####
###############################
def open_fds_file():
    # DESCRIPTION:
    #  checks if an FDS file is already open, closes it if necessary and opens a new one
    #  as specified by the outfile variable, writes a HEAD statement via write_to_fds
    if type(vars['fds_file']) == file:
        close_fds_file()
    vars['fds_file'] = open(vars['outfile'], 'w')
    write_to_fds("&HEAD CHID='%s', TITLE='%s' /\n"%(vars['chid'], vars['title']))
    # end open_fds_file

def write_to_fds(text):
    # DESCRIPTION:
    #  checks if the FDS file specified by the fds_file variable exists, opens a new one
    #  via open_fds_file if necessary and writes a given text into the FDS file
    # INPUT:
    #  text     - text to write into the FDS file
    if type(vars['fds_file']) != file:
        open_fds_file()
    vars['fds_file'].write(text)
    # end write_to_fds

def close_fds_file():
    # DESCRIPTION:
    #  writes a TAIL statement via write_to_fds and closes the FDS file
    write_to_fds("&TAIL/\n")
    vars['fds_file'].close()
    # end close_fds

###############################
##### FDS FILE GENERATION #####
###############################
def info(node):
    # DESCRIPTION:
    #  writes a short info about the job to standard output and creates a new FDS file via open_fds_file
    # INPUT (arguments of node):
    #  chid     - job identifier (required)
    #  title    - short description of the job (optional)
    #  outfile  - name of the FDS file, should match with chid (required)
    if check_val(node, ['chid','outfile'], opt=False):
        vars['chid'] = get_val(node,"chid")
        vars['title'] = get_val(node,"title", opt=True)
        vars['outfile'] = get_val(node,"outfile")
        print "chid    : %s"%vars['chid']
        print "title   : %s"%vars['title']
        print "outfile : %s"%vars['outfile']
        open_fds_file()
    # end info

def mesh(node):
    # DESCRIPTION:
    #  creates a mesh and writes the MESH statement via write_to_fds
    # INPUT (arguments of node):
    #  px, py, pz                                       - number of meshes in x,y or z direction (?) (default: 1)
    #  gnx, gny, gnz                                    - ? (optional)
    #  gxmin, gxmax, gymin, gymax, gzmin, gzmax         - ? (optional)

    nmeshes = 1
    px = 1
    py = 1
    pz = 1
    if check_val(node, ["px", "py", "pz"]):
        px = get_val(node, "px", opt=True)
        py = get_val(node, "py", opt=True)
        pz = get_val(node, "pz", opt=True)

    nmeshes = px * py * pz      # NOT USED

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
    # end mesh

def obst(node):
    # DESCRIPTION:
    #  defines an rectangular obstacle and writes the OBST statement via write_to_fds
    # INPUT (arguments of node):
    #  x1, y1, z1       - coordinates of one corner of the obstacle
    #  x2, y2, z2       - coordinates of the opposing corner of the obstacle
    #  color            - color of the obstacle
    #  surf_id          - surface of the obstacle
    #  comment          - comment to be written after the OBST statement

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
    # end obst

def hole(node):
    # DESCRIPTION:
    #  defines an rectangular hole in an obstacle and writes the HOLE statement via write_to_fds
    # INPUT (arguments of node):
    #  x1, y1, z1       - coordinates of one corner of the hole
    #  x2, y2, z2       - coordinates of the opposing corner of the hole

    write_to_fds("&HOLE XB=%f,%f,%f,%f,%f,%f /\n"%(eval(node.attrib["x1"], {}, vars),
                                                   eval(node.attrib["x2"], {}, vars),
                                                   eval(node.attrib["y1"], {}, vars),
                                                   eval(node.attrib["y2"], {}, vars),
                                                   eval(node.attrib["z1"], {}, vars),
                                                   eval(node.attrib["z2"], {}, vars)))
    # end hole

#############################
##### COMBINED COMMANDS #####
#############################
def bounded_room(node):
    # DESCRIPTION:
    #  creates a simple rectangular room with walls and a fitting mesh created via mesh
    # INPUT (arguments of node):
    #  x1, y1, z1                       - coordinates of one corner of the room (optional)
    #  x2, y2, z2                       - coordinates of the opposing corner of the room (optional)
    #  bx1, bx2, by1, by2, bz1, bz2     - wall thickness in relation to wt (default: 0)
    #  wt                               - reference value for wall thickness (default: 0.0)
    #  ax, ay, az                       - number of meshes in the x, y or z direction (default: 1)
    #  delta                            - cell width of the mesh? (optional)

    # get input values from node (if possible)
    x1 = get_val(node, "x1", opt=True)
    x2 = get_val(node, "x2", opt=True)
    y1 = get_val(node, "y1", opt=True)
    y2 = get_val(node, "y2", opt=True)
    z1 = get_val(node, "z1", opt=True)
    z2 = get_val(node, "z2", opt=True)

    bx1 = check_get_val(node, "bx1", 1)
    bx2 = check_get_val(node, "bx2", 1)
    by1 = check_get_val(node, "by1", 1)
    by2 = check_get_val(node, "by2", 0)
    bz1 = check_get_val(node, "bz1", 0)
    bz2 = check_get_val(node, "bz2", 0)

    wt = check_get_val(node, "wt", 1.0)

    ax = check_get_val(node, "ax", 1)
    ay = check_get_val(node, "ay", 1)
    az = check_get_val(node, "az", 1)

    delta = get_val(node, "delta", opt=True)

    # compute the minimum mesh size (room + walls)
    dxmin = x1 - bx1*wt
    dxmax = x2 + bx2*wt
    dymin = y1 - by1*wt
    dymax = y2 + by2*wt
    dzmin = z1 - bz1*wt
    dzmax = z2 + bz2*wt

    # compute required number of mesh cells
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

    # save the computed values as global variables (for further use, if necessary)
    add_var("xmin", dxmin)
    add_var("xmax", dxmax)
    add_var("ymin", dymin)
    add_var("ymax", dymax)
    add_var("zmin", dzmin)
    add_var("zmax", dzmax)

    add_var("nx", nx)
    add_var("ny", ny)
    add_var("nz", nz)


    # call the mesh method
    mesh(node)

    # draw the walls if the wall is thicker than 0
    write_to_fds("&OBST XB=%f,%f,%f,%f,%f,%f, COLOR='WHITE', TRANSPARENCY=0.75 /\n"%(
                             x1, x2, y1, y2, z1, z2))
    if wt*bx1>epsilon:
         write_to_fds("&OBST XB=%f,%f,%f,%f,%f,%f, COLOR='FIREBRICK', TRANSPARENCY=0.5 /\n"%(
                             x1-wt*bx1, x1, y1-wt*by1, y2+wt*by2, z1-wt*bz1, z2+wt*bz2))
    if wt*bx2>epsilon:
         write_to_fds("&OBST XB=%f,%f,%f,%f,%f,%f, COLOR='FIREBRICK', TRANSPARENCY=0.5 /\n"%(
                             x2, x2+wt*bx2, y1-wt*by1, y2+wt*by2, z1-wt*bz1, z2+wt*bz2))
    if wt*by1>epsilon:
         write_to_fds("&OBST XB=%f,%f,%f,%f,%f,%f, COLOR='FIREBRICK', TRANSPARENCY=0.5 /\n"%(
                             x1-wt*bx1, x2+wt*bx2, y1-wt*by1, y1, z1-wt*bz1, z2+wt*bz2))
    if wt*by2>epsilon:
         write_to_fds("&OBST XB=%f,%f,%f,%f,%f,%f, COLOR='FIREBRICK', TRANSPARENCY=0.5 /\n"%(
                             x1-wt*bx1, x2+wt*bx2, y2, y2+wt*by2, z1-wt*bz1, z2+wt*bz2))
    if wt*bz1>epsilon:
         write_to_fds("&OBST XB=%f,%f,%f,%f,%f,%f, COLOR='FIREBRICK', TRANSPARENCY=0.5 /\n"%(
                             x1-wt*bx1, x2+wt*bx2, y1-wt*by1, y2+wt*by2, z1-wt*bz1, z1))
    if wt*bz2>epsilon:
         write_to_fds("&OBST XB=%f,%f,%f,%f,%f,%f, COLOR='FIREBRICK', TRANSPARENCY=0.5 /\n"%(
                             x1-wt*bx1, x2+wt*bx2, y1-wt*by1, y2+wt*by2, z2, z2+wt*bz2))
    # end bounded_room

def my_room(node):
    # DESCRIPTION:
    #  subset of bounded_room
    #  determines mesh parameters for simple rectangular room with walls but does neither create the mesh nor the walls
    # INPUT (arguments of node):
    #  x1, y1, z1                       - coordinates of one corner of the room (optional)
    #  x2, y2, z2                       - coordinates of the opposing corner of the room (optional)
    #  bx1, bx2, by1, by2, bz1, bz2     - wall thickness in relation to wt (default: 0)
    #  wt                               - reference value for wall thickness (default: 0.0)
    #  ax, ay, az                       - number of meshes in the x, y or z direction (default: 1)
    #  delta                            - cell width of the mesh? (optional)
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
    # end my_room

############
# UNSORTED #
############

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
    if check_val(node, 'id', opt=True):
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


def ramp(node):
	if 'id' in node.attrib:
		id = eval(node.attrib['id'], {}, vars)
		ramp = "&RAMP ID='RAMP_%s'"%id

	if 't' in node.attrib:
		t = eval(node.attrib['t'], {}, vars)
	if 'f' in node.attrib:
		f = eval(node.attrib['f'], {}, vars)

		ramp += "T=%f, F=%f /\n"%(t, f)

		write_to_fds(ramp)


def radi(node):

	if 'radiative_fraction' in node.attrib:
		rf = eval(node.attrib['radiative_fraction'], {}, vars)
		radi = "&RADI RADIATIVE_FRACTION = %f /\n"%rf

		write_to_fds(radi)



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
    check_val(node, ["var"], opt=False)

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
    check_val(node, ["q" ,"id"], opt=False)
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
