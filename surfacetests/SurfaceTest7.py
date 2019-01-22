from __future__ import division

import bls, ktransit, math, pylab, os, batman, untrendy, csv

import numpy as np

from scipy.stats import gamma

from astropy.io import fits

import matplotlib.pyplot as plt
#fig = plt.figure()
#axes = plt.gca()

import pylab
from pylab import xlabel, ylabel, title, plot, show, ylim, xlim

from astropy.stats import sigma_clip

from ktransit import FitTransit

from scipy import signal

import PyAstronomy
from PyAstronomy import pyasl

from numpy import mean, sqrt, square, arange



bestFperarr = []
bestFrprsarr = []
SDEarr = []
diffarr = []
targetnamearr = []

tested_rprs = []
tested_period = []
recovered_rprs = []
recovered_period = []

rprsarr = []
lowarr = []

recoveredarr = []
SNR = []

time = []
flux = []

SNRforLC = []

QCDPParr = []


fig, ax = plt.subplots(1, 1, figsize=[15,10])

#ax.hold(True)

filecount = sum(1 for line in open('all_txt_files.txt'))

for x in range(1):

#opens list of file names, creates list of file names
    with open('all_txt_files.txt') as f:
        content = f.readlines()

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
    #title('EPIC ' + targetname + ' Light Curve')
    
        print("TARGET: EPIC " + str(targetname))
    
        campaign_no = file[37:]
        campaign_no = campaign_no[:-31]
        print("CAMPAIGN " + str(campaign_no))
    
#normalize to 0.0
        flux = [i-1 for i in flux]



        flux = np.asarray(flux)
        time = np.asarray(time)


        
#SIGMA CLIPPING
        flux = sigma_clip(flux, sigma=4, iters=1)
        
    #uncomment if extra time stamp
        #time.pop()

    
##########################
#IMPORT CDPP FROM FITS
##########################
        f = fits.open('/Users/sheilasagear/OneDrive/K2_Research/Cycle2_FITS/CYCLE2FITS/hlsp_k2sff_k2_lightcurve_' + str(targetname) + '-c0' + str(campaign_no) + '_kepler_v1_llc.fits')

        bestaper = f[1].data
        besthead = f[1].header
        
        QCDPP = besthead['QCDPP6']
        print(QCDPP)
        QCDPParr.append(QCDPP)


        RMS = sqrt(mean(square(flux)))


    



        T0 = 1.0 #np.random.uniform(low=.01, high=1)
    
        period = np.random.uniform(low=1, high=26)
        tested_period.append(period)

        print(period)
        
        impact = 0.0 #np.random.uniform(low=0.0, high=1.0)
        
        rprs = np.random.uniform(low=.05, high=1.0)
        tested_rprs.append(rprs)

        
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
            T0=T0,     # a transit mid-time  
            period=period, # an orbital period in days
            impact=impact, # an impact parameter
            rprs=rprs,   # planet stellar radius ratio  
            ecosw=0.0,  # eccentricity vector
            esinw=0.0,
            occ=0.0)    # a secondary eclipse depth in ppm

        M.add_data(time=np.array(time[:]))      # integration time of each timestamp

        tmod = M.transitmodel # the out of transit data will be 0.0 unless you specify zpt


    #plt.plot(M.time,tmod)
    #plt.show()






    

        if len(tmod) != len(flux):
            flux = flux[0:len(flux)-1]
        
        merged_flux = tmod + flux

        length = len(merged_flux)


    
    #mergedfluxDetrend, ferr = untrendy.untrend(time, merged_flux)

        trend, ferr = untrendy.untrend(time, flux)

        """
        
        mergedfluxDetrend = list()
                
        for i in range(len(trend)):
            val = merged_flux[i]-merged_flux[i-1]
            mergedfluxDetrend.append(val)

        """
        mergedfluxDetrend = []
        
        for x in range(length):
            mergedfluxDetrend.append(merged_flux[x]-trend[x])

        #mergedfluxDetrend = sigma_clip(mergedfluxDetrend, sigma = 3, iters=1)

        u = [0.0]*len(time)
        v = [0.0]*len(time)

        u = np.array(u)
        v = np.array(v)

    #time, flux, u, v, number of freq bins (nf), min freq to test (fmin), freq spacing (df), number of bins (nb), min transit dur (qmi), max transit dur (qma)

        nf = 1000.0
        fmin = .035
        df = 0.001
        nbins = 300
        qmi = 0.001
        qma = 0.3
    
        results = bls.eebls(time, merged_flux, u, v, nf, fmin, df, nbins, qmi, qma)
            
#RESULTS:
#power, best_period, best_power, depth, q, in1, in2
#0      1            2           3      4  5    6

        print('BLS period: ' + str(results[1]))


        SR_array = results[0]
        max_SR = max(SR_array)
        avg_SR = np.mean(SR_array)
        sd_SR = np.std(SR_array)

#normalize SR_array between 0 and 1
        SR_array = [i/max_SR for i in SR_array]

    #print(max_SR, avg_SR, sd_SR)

#np.arange(freq start, freq stop (must be calculated), df (freq step))
    #freq = np.arange(.2, 1.2, .001, dtype=None)

        freq = fmin + np.arange(nf) * df

        #plt.clf()

    #plt.plot(freq, SR_array)
    #plt.title('EPIC ' + str(targetname))
    #plt.show()


        SDE = (max_SR-avg_SR)/sd_SR
    
        print('Signal Detection Efficiency: ' + str(SDE))
        if SDE >= 6:
            print('SDE above 6: Transit Detectable')
        #detect_count += 1
                #detect_SDE.append(SDE)
                #detect_per.append(p)
                #detect_rad.append(r)
                #detect_BLS_per.append(results[1])
            SDEarr.append(True)
                
                #detect_diff.append(results[1]-p)
        else:
            print('SDE below 6: Transit Undetectable')
                #undetect_count += 1
                #undetect_SDE.append(SDE)
                #undetect_per.append(p)
                #undetect_rad.append(r)
                #undetect_diff.append(results[1]-p)
            SDEarr.append(False)



##########################
#Folding and Binning
##########################

    #pylab.cla()

        f0 = 1.0/results[1]
        n = len(time)
        ibi = np.zeros(nbins)
        y = np.zeros(nbins)
        phase = np.linspace(0.0, 1.0, nbins)
        for i in range(n):
            ph = u[i]*f0
            ph = ph-int(ph)
            j = int(nbins*ph)
            ibi[j] = ibi[j] + 1.0
            y[j] = y[j] + v[i]
    #binned and folded plot
    #pylab.cla()
    #plt.scatter(phase, y/ibi, s=3)
    #plt.title("EPIC " + str(targetname) + " folded and binned LC")
    #pylab.show()




        mergedfluxDetrend = np.asarray(mergedfluxDetrend)



        #raise SystemExit(0)

        phases = PyAstronomy.pyasl.foldAt(time, results[1], getEpoch = False)

        sortPhase = np.argsort(phases)
        phases = phases[sortPhase]
        mergedfluxFolded = merged_flux[sortPhase]


        

###########################
#BLS Overlay
###########################

        
        high = results[3]*results[4]
        low = high - results[3]
        
        fit = np.zeros(nbins) + high # H
        fit[results[5]:results[6]+1] = low # L


    #plt.plot(phase, fit)
    #plt.xlabel(r"Phase")
    #plt.ylabel(r"Mean value of flux")
    #plt.title("SDE " + str(SDE) + "; BLS period " + str(results[1]))
    #plt.ylim(-.1, .1)
    #pylab.savefig("/Users/sheilasagear/OneDrive/K2_Research/bls-ktransit/Pipeline/EPIC229227254-2sigclip/Period" + str(p) + "Radius" + str(r) + "/folded_pltPer" + str(p) + "Rad" + str(r) + 'BLSoverlay.png')




##########################
#Detrending Flux and Levenberg-Marquardt Fitting:
#if SDE>6 
##########################



        fitT = FitTransit()
        fitT.add_guess_star(rho=1.5)    
        fitT.add_guess_planet(
            period=results[1], impact=0.0, 
            T0=1.0, rprs=0.5)#need a guess rprs
        fitT.add_data(time=time, flux=mergedfluxDetrend)
                
                    
        vary_star = ['rho']      # not sure how to avoid free stellar parameters? ideally would not vary star at all
        vary_planet = (['period', 'rprs'])
                    
        fitT.free_parameters(vary_star, vary_planet)
        fitT.do_fit()

    #print(fitT.fitresultstellar.items())
    #print(fitT.fitresultplanets.items())
                    
    #bestFstellar = fitT.fitresultstellar.items()
    #bestFrho = bestFstellar[0][1]#Best Fit Rho
            
        bestFplanet = fitT.fitresultplanets.items()
        bestFperiod = bestFplanet[0][1]['period']#Best Fit Period
        bestFrprs = bestFplanet[0][1]['rprs']#Best Fit rprs
    #bestFimpact = bestFplanet[0][1]['impact']
    #bestFT0 = bestFplanet[0][1]['T0']
                    
        fitT.print_results()






        #color for outliers

        q = untrendy.median(time, flux)


        f, ((ax1, ax2), (ax3, ax4)) = plt.subplots(nrows=2, ncols=2, figsize=(11, 5))
#fig.subplots_adjust(hspace=.01)

        bbox_props = dict(boxstyle="square,pad=0.4", facecolor='none', edgecolor='black')

        ax1.scatter(time, flux, color='k', s=2)
        ax1.plot(time, q, color='mediumaquamarine')
        ax1.set_xlabel('Time (days)')
        ax1.set_ylabel('Normalized Flux')
        ax1.set_title('EPIC ' + str(targetname))


        ax2.plot(freq, SR_array, color='black')
        ax2.set_ylabel('Power')
        ax2.set_xlabel('Frequency')
        ax2.set_title('Box Least-Squares')
        ax2.set_ylim(0, 1.3)
        ax2.text(0.2, .9, 'SDE: ' + str(SDE) + '\n' + 'RMS: ' + str(RMS) + '\n' + 'BLS Period: ' + str(results[1]) + '\n' + 'Injected Period: ' + str(period), bbox=bbox_props, fontsize=7)



        ax3.scatter(phases, mergedfluxFolded, color='k', s=2)
        ax3.set_xlabel('Phase')
        ax3.set_ylabel('Normalized Flux')
        ax3.set_title('Phase Folded: Period ' + str(results[1]))

        """
        ax4.scatter(time, fluxDetrend, color='k', s=2)
        ax4.plot(time, fitT.transitmodel, color='mediumaquamarine')
        ax4.set_ylim(-0.25,0.25)

        ax4.set_xlabel('Time (days)')
        ax4.set_ylabel('Detrended Flux')
        ax4.set_title('Levenberg-Marquardt')
        #ax4.annotate('Best fitting planet parameters: ' + '\n' + 'Period: ' + str(bestFperiod) + '\n' + 'RPRS: ' + str(bestFrprs), xy = (time[1], 0.04), bbox = bbox_props)
        ax4.text(time[1], 0.12, 'Best fitting planet parameters: ' + '\n' + 'Period: ' + str(bestFperiod) + '\n' + 'RPRS: ' + str(bestFrprs), bbox=bbox_props, fontsize=7)
        """


        plt.tight_layout()
        f.savefig(r'/Users/sheilasagear/Dropbox/ssagear_k2/cycle2/injections/EPIC' + str(targetname) + 'period' + str(period) + 'rprs' + str(rprs) + '.png')


        """
        fig.clf()

        fig, ax = plt.subplots(1, 1, figsize=[15,10])
        
        if abs(bestFperiod-period) < 2:
            recovered = True
            recoveredarr.append(True)
            ax.scatter(period, QCDPP, c='b', s=3)

        else:
            recovered = False
            recoveredarr.append(False)
            ax.scatter(period, QCDPP, c='r', s=3)

        """


        
        tempindex+=1
        

####################
#END LOOP
####################
"""
ax.set_ylabel('QCDPP')
ax.set_xlabel('Period')
ax.set_title('Per vs QCDPP (blue=recovered)')

show()
"""

#fig.savefig(r'/Users/sheilasagear/Desktop/temp2.png')