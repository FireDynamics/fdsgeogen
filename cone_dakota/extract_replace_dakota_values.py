import sys

f_params = open(sys.argv[1],"r")
f_template = open(sys.argv[2],"r")

first_line = f_params.readline().rstrip('\n').split()

no_vars = int(first_line[0])
var_dict = {}

for i in range(no_vars):
    line = f_params.readline().rstrip('\n').split()
    var_name  = line[1]
    var_value = float(line[0])
    #print "found variable (%s) with value (%f)"%(var_name,var_value)
    var_dict[var_name] = var_value
    
#print var_dict

for line in f_template:
    for key in var_dict:
        line = line.replace("#%s#"%key, "%f"%var_dict[key]).rstrip('\n')
        
    print line
    
