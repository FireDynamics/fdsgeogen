import sys
import scipy.optimize
import numpy as np

import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt


def hrr_model(t, t0, t1, a1, a2, b1):
    
    rv = np.copy(t)
    #rv[t <= t0] = a1/fa1*(np.exp(a2/fa2*t[t <= t0]) - 1.0)
    rv[t <= t0] = 0.0
    rv[(t > t0) & (t <= t1)] = a1*(t[(t > t0) & (t <= t1)]-t0)** a2
    rv[t  > t1] = b1

    return rv

def errfunction(params, t, hrr_data):
    t0 = params[0]
    t1 = params[1]    
    a1 = params[2] 
    a2 = params[3] 
    b1 = params[4]    
    
    err = hrr_model(t, t0, t1, a1, a2, b1) - hrr_data
    
    return err
    
def compute_ignition(t, hrr_data):
    init_par = [0, 1, 1, 1]
    best_par = init_par
    min_val  = 1e16

    for gt0 in np.linspace(t[10], t[-10], 25):
        for gt1 in np.linspace(t[0], gt0, 25):

            init_par = [gt0, gt1, 1, 2, 1]

            cur_pars, conv_x, infodict, mesg, rc = scipy.optimize.leastsq(errfunction, init_par[:], args=(t, hrr_data), full_output=True, epsfcn=0.01)
            cur_err = np.sum(errfunction(cur_pars, t, hrr_data)**2)
            if cur_err < min_val:
                best_par = cur_pars
                min_val  = cur_err
                #print "found new best par at gt0=%f, gt1=%f, res=%f"%(gt0, gt1, cur_err)

    #print "best parameter:", best_par, min_val

    t0 = best_par[0]
    t1 = best_par[1]
    b1 = best_par[4]
    
    #t_ign = (t1-t0)*0.5 + t0
    t_ign = t[np.where(hrr_model(t, *best_par)>0.2*b1)[0][0]]


    t_end = t[-1]
    trust = 1
        
    if t1>0.8*t_end: trust = 0
    if (t1-t0)<0.1: trust = 0

    #print "ignition time: ", t_ign
    #print "trust: ", trust
    
    print t_ign, "  ", trust
    
    return best_par, t_ign, trust
    
def plot_hrr_data_model_ignition(t, hrr_data, hrr_model, t_ign):
    plt.plot(t, hrr_data, label='data')
    plt.plot(t, hrr_model, label='fit')
    plt.axvline(t_ign, color='r')


    #plt.ylabel("integral of burning rate [kg / s / m^2]")
    plt.ylabel("heat release rate [kW]")
    plt.xlabel("time [s]")
    plt.legend()
    plt.savefig("integral.pdf")
    plt.clf()    

def simulate_simulation(data):
    t_igns = []
    ts = []
    trusts = []

    for il in np.linspace(0.1*len(data), len(data)-1, 25):
    
        cil = int(il)

        print "select up to index %d of %d"%(cil, len(data))

        t = data[:cil,0]
        hrr_data = data[:cil,1]

        p, t_ign, trust = compute_ignition(t, hrr_data)

        ts.append(t[-1])
        t_igns.append(t_ign)
        trusts.append(trust)

    plt.plot(ts, t_igns, label="ignition time")
    plt.plot(ts, trusts, label="trust")    
    plt.ylabel("ignition time [s]")
    plt.xlabel("simulation time [s]")
    plt.legend()
    plt.savefig("simulation.pdf")
    plt.clf()


#############################################

data = np.loadtxt(sys.argv[1], skiprows=2, usecols=(0,1), delimiter=',')    

t = data[:,0]
hrr_data = data[:,1]
p, t_ign, trust = compute_ignition(t, hrr_data)
plot_hrr_data_model_ignition(t, hrr_data, hrr_model(t, *p), t_ign)

#simulate_simulation(data)







