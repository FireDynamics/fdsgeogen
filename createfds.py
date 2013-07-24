import sys
import xml.etree.ElementTree as ET


tree = ET.parse(str(sys.argv[1]))
root = tree.getroot()

nodes = root.findall(".")

vars = {}

for node in root.iter('const'):
    print node
    print node.tag
    print node.attrib
    
    if node.tag == 'const':
        for att in node.attrib:
            print att
            print node.attrib[att]
            vars[att] = float(node.attrib[att])
            

for node in root.iter('eval'):
    print node
    print node.tag
    print node.attrib
    
    for att in node.attrib:
         vars[att] = eval(node.attrib[att], globals(), vars)

print vars

for node in root.iter('obst'):
    print node
    print node.tag
    print node.attrib
    
    print "OBST XB=%f,%f,%f,%f,%f,%f"%(eval(node.attrib["x1"], globals(), vars),
                                       eval(node.attrib["x2"], globals(), vars),
                                       eval(node.attrib["y1"], globals(), vars),
                                       eval(node.attrib["y2"], globals(), vars),
                                       eval(node.attrib["z1"], globals(), vars),
                                       eval(node.attrib["z2"], globals(), vars))

for node in root.iter('loop'):
    print node
    print node.tag
    print node.attrib
    
    loop_var = {node.attrib['var'] : int(node.attrib['start'])}
    
    print loop_var
    print dict(vars.items() + loop_var.items())
    print vars
