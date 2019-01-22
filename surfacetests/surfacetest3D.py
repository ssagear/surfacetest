




from __future__ import division

import bls, ktransit, math, pylab, os, batman

from scipy.stats import gamma

import untrendy

from astropy.io import fits

import numpy as np

import matplotlib.pyplot as plt
#fig = plt.figure()
#axes = plt.gca()

from mpl_toolkits.mplot3d import Axes3D
##axe = Axes3D(plt.gcf())
#ax = fig.add_subplot(111, projection='3d')

from matplotlib import pyplot
import pylab
from pylab import xlabel, ylabel, title, plot, show, ylim, xlim

from astropy.stats import sigma_clip

#fige = pylab.figure()
#ax = Axes3D(fig)

from ktransit import FitTransit

from scipy import signal

import obspy
from obspy.signal.detrend import polynomial

perarr = []
radarr = []
bestFperarr = []
bestFrprsarr = []
SDEarr = []
diffarr = []
targetnamearr = []




##########################
#INITIALIZATION
##########################

#Depending on step size and limits:
#detect_x and undetect_x are a maximum of 95*199 = 18905
#Radius ratio from .05 to 1 with a step size of .01
#Period from .1 to 20 days with a step size of .1

detect_count = 0
detect_SDE = []*18905
detect_per = []*18905
detect_rad = []*18905
detect_BLS_per = []*18905

undetect_count = 0
undetect_SDE = []*18905
undetect_per = []*18905
undetect_rad = []*18905

detect_diff = []*18905
undetect_diff = []*18905

diff = [[0 for x in range(96)] for y in range(200)]

maskindex = []


rad_diff_values = [[] for y in range(96)]
per_diff_values = [[] for y in range(200)]

###########################################
#These limits and step size can be changed!
rad_range = np.arange(.3, .4, .1)
per_range = np.arange(5, 6, 1)
###########################################


total_rad = len(rad_range)
total_per = len(per_range)
total = total_rad*total_per

recoveredforLC = []
frac_recovered = []
SNR = []





##########################
#BEGIN LOOP
##########################

#LATER: loop through C6 and C7 light curves; open and inject range of transits into each 

#count number of files being graphed
filecount = sum(1 for line in open('all_txt_files.txt'))

#opens list of file names, creates list of file names
with open('all_txt_files copy.txt') as f:
    content = f.readlines()


    recovered = 0
    SNRforLC = []
#converts each file name to string, removes \n from end, opens each object's txt file (loop)
#and stores (x,y) in list 'data'
tempindex = 0
while (tempindex < filecount):
    file = str(content[tempindex])
    file = file.strip('\n')
    file = file.strip('\r')

    with open(file) as f:
        data1 = f.read()

#converts txt file to string (and removes heading: 30 characters) 
#in order to isolate each (x,y) coordinate as an element in list 'data'
    datastr = str(data1)
    datastr = datastr[30:]
    data1 = datastr.split('\n')


#removes comma after each (x,y) coordinate;
#islates x and y values as indicies of list 'data'
    index = -1
    while (index < len(data1)):
        tempstring = str(data1[index])
        data1[index] = tempstring.rstrip(',')
        data1[index] = tempstring.split(', ')
        index+=1
    data1.pop

    data2 = sum(data1, [])
    
    index = 0
    while (index < len(data2)):
        if index % 2 == 1:
            data2[index] = data2[index].rstrip(',')
        index+=1
    data2.pop()
    
#convers str data points to float
    data_final = [float(i) for i in data2]

#defines x and y values by index of 'data'
    time = data_final[0::2]
    flux = data_final[1::2]

#normalizes flux values to 1.0 (at avg of flux values)
    flux_count = len(flux)
    sumflux = sum(flux)
    flux_avg = sumflux/flux_count
        
    flux = [i/flux_avg for i in flux]

#targets titled by EPIC names
    targetname = file[25:]
    targetname = targetname[:-35]
    title('EPIC ' + targetname + ' Light Curve')
    
    print("TARGET: EPIC " + str(targetname))
        
    campaign_no = file[37:]
    campaign_no = campaign_no[:-31]
    print("CAMPAIGN " + str(campaign_no))
    
#normalize to 0.0
    flux = [i-1 for i in flux]


#SIGMA CLIPPING
    flux = sigma_clip(flux, sigma=3, iters=1)
        
#uncomment if extra time stamp
    time.pop()

    flux = flux.filled(fill_value=0)


################################################################

    rindex = -1
    pindex = -1

    for r in rad_range:
        rindex += 1
        pindex = -1
        for p in per_range:
            pindex += 1


        
##########################
#Create ktransit Data: CODE FROM GITHUB
##########################

            num_time = len(time)
            
            M = ktransit.LCModel()
            M.add_star(
            rho=1.5, # mean stellar density in cgs units
            ld1=0.2, # ld1--4 are limb darkening coefficients 
            ld2=0.4, # if only ld1 and ld2 are non-zero then a quadratic limb darkening law is used
            ld3=0.0, # if all four parameters are non-zero we use non-linear flavour limb darkening
            ld4=0.0, 
            dil=0.0, # a dilution factor: 0.0 -> transit not diluted, 0.5 -> transit 50% diluted
            zpt=0.0  # a photometric zeropoint, incase the normalisation was wonky
                )
            M.add_planet(
                T0=3.0,     # a transit mid-time  
            period=p, # an orbital period in days
            impact=0.0, # an impact parameter
            rprs=r,   # planet stellar radius ratio  
            ecosw=0.0,  # eccentricity vector
            esinw=0.0,
            occ=0.0)    # a secondary eclipse depth in ppm
            

            M.add_data(time=np.array(time[:])),

            tmod = M.transitmodel# the out of transit data will be 0.0 unless you specify zpt
            #pylab.cla()


            
################################################################


            if len(tmod) != len(flux):
                flux = flux[0:len(flux)-1]
            
            merged_flux = tmod + flux

            mergedfluxDetrend, ferr = untrendy.untrend(time, merged_flux)

            trend, ferr = untrendy.untrend(time, flux)

            mergedfluxDetrend = list()
                
            for i in range(len(trend)):
                val = merged_flux[i]-merged_flux[i-1]
                mergedfluxDetrend.append(val)

################################################################

            u = [0.0]*len(time)
            v = [0.0]*len(time)

            u = np.array(u)
            v = np.array(v)

            nbins = 200
        
            results = bls.eebls(time, mergedfluxDetrend, u, v, 1000.0, .1, .001, nbins, .001, .3)
            
#RESULTS:
#power, best_period, best_power, depth, q, in1, in2
#0      1            2           3      4  5    6

            print('rprs: ' + str(r))
            print('BLS period: ' + str(results[1]))
            print('Set period: ' + str(p))

            
################################################################



            SR_array = results[0]

            max_SR = max(SR_array)
            avg_SR = np.mean(SR_array)
            sd_SR = np.std(SR_array)

#normalize SR_array between 0 and 1
            SR_array = [i/max_SR for i in SR_array]

             #print(max_SR, avg_SR, sd_SR)

#np.arange(freq start, freq stop (must be calculated), df (freq step)
            freq = np.arange(.3, 1.3, .001, dtype=None)


            
################################################################

            SDE = (max_SR-avg_SR)/sd_SR
            
            print('Signal Detection Efficiency: ' + str(SDE))
            if SDE >= 6:
                print('SDE above 6: Transit Detectable')
                detect_count += 1
                detect_SDE.append(SDE)
                detect_per.append(p)
                detect_rad.append(r)
                detect_BLS_per.append(results[1])
                
                detect_diff.append(results[1]-p)
            else:
                print('SDE below 6: Transit Undetectable')
                undetect_count += 1
                undetect_SDE.append(SDE)
                undetect_per.append(p)
                undetect_rad.append(r)
                undetect_diff.append(results[1]-p)

            diff[pindex][rindex] = (results[1]-p)
            print('Difference in period is '+ str(diff[pindex][rindex]))
            print('\n')
            


################################################################

    tempindex += 1




for i in range(len(detect_SDE)):
    if detect_SDE[i] == 0:
        del detect_SDE[i]

for i in range(len(detect_per)):
    if detect_per[i] == 0:
        del detect_per[i]

for i in range(len(detect_rad)):
    if detect_rad[i] == 0:
        del detect_rad[i]

for i in range(len(undetect_SDE)):
    if undetect_SDE[i] == 0:
        del undetect_SDE[i]

for i in range(len(undetect_per)):
    if undetect_per[i] == 0:
        del undetect_per[i]

for i in range(len(undetect_rad)):
    if undetect_rad[i] == 0:
        del undetect_rad[i]


f, ax = plt.subplots(nrows=1, ncols=1, figsize=(11, 5), projection='3d')
ax.plot_surface(detect_per, detect_rad, detect_diff, zdir='z', s=5, c=detect_SDE)
show()
