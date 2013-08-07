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
        vars['chid'] = node.attrib['chid']
        print "chid: %s"%vars['chid']

    if 'outfile' in node.attrib: 
        vars['outfile'] = node.attrib['outfile']
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
    write_to_fds(vars,"&MESH IJK=%d,%d,%d, XB=%f,%f,%f,%f,%f,%f /\n"%(
                        eval(node.attrib["nx"], {}, vars),
                        eval(node.attrib["ny"], {}, vars),
                        eval(node.attrib["nz"], {}, vars),
                        eval(node.attrib["xmin"], {}, vars),
                        eval(node.attrib["xmax"], {}, vars),
                        eval(node.attrib["ymin"], {}, vars),
                        eval(node.attrib["ymax"], {}, vars),
                        eval(node.attrib["zmin"], {}, vars),
                        eval(node.attrib["zmax"], {}, vars)))

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


tree = ET.parse(str(sys.argv[1]))
root = tree.getroot()

vars = {'outfile':"output.fds", 'chid':"chid", 'title':"title", 'fds_file_open':False, 'fds_file':0}

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

close_fds_file(vars)
