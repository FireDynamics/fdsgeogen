import numpy as np
import matplotlib.pyplot as plt

data = np.loadtxt("rundir/fgg_example_10_hrr.csv", skiprows=2, delimiter=',')

plt.plot(data[:,0], data[:,1])
plt.ylabel('hrr [kW]')
plt.xlabel('time [s]')
plt.savefig("e10-hrr.pdf")
plt.clf()

plt.plot(data[:,0], data[:,12])
plt.ylabel('mlr [kg/s]')
plt.xlabel('time [s]')
plt.savefig("e10-mlr.pdf")
plt.clf()

plt.plot(data[:,0], data[:,1], label='hrr')
plt.plot(data[:,0], data[:,12]*4.5e4, label='mlr')
plt.ylabel('hrr [kW] -- mlr [2e-5 kg/s]')
plt.xlabel('time [s]')
plt.legend()
plt.xlim([0,25])
plt.savefig("e10-hrr-mlr.pdf")
plt.clf()