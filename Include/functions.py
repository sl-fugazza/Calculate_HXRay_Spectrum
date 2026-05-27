import config

import numpy as np
import sys, os
import matplotlib.pyplot as plt 

from scipy.interpolate import interp1d, CubicSpline

def importCoordinates(r_filename, t_filename):
    r = np.loadtxt(config.simPath + r_filename)
    t = np.loadtxt(config.simPath + t_filename)
    return r, t

def importSpecies(ionName, Z, filename):
    
    IonDensity = np.loadtxt(config.simPath + filename)
    species = [ionName, IonDensity, Z]
    
    return species

def importREdensity(filename):
    REdensity = np.loadtxt(config.simPath + filename)
    return REdensity


def importFirstWall():
    Rw, Zw = np.loadtxt(config.simPath + "../firstWall_ITER.txt", unpack=True)
    return Rw, Zw



def attenuateSpectrum(spectrum, Ehxr, materials):

    

    newSpectrum = spectrum
    for mat_key, mat_values in materials.items():
        print("Applyng attenuation of " + mat_key + " to the spectrum")
        nameFile, thickness = mat_values[0], mat_values[1]*1e2 # centimetres
        
        E_phot, mu = np.loadtxt("./Data/attenuationCoefficients/"+nameFile, 
                                unpack = True, skiprows=1)
        # checking and fixing the energy vector of the photons:
        # there can be a K-shell jump
        for i in range(len(E_phot)-1):
            if E_phot[i] >= E_phot[i+1]: # in principle, using == should work, but let's be safe
                E_phot[i+1] = E_phot[i]+ 0.01*E_phot[i] # just 1 percent bigger

        # cs = interp1d(E_phot, mu, kind='linear')
        cs = CubicSpline(E_phot, mu)
        new_mu = cs(Ehxr) # value of mu corresponding to the energy bin of the spectrum


        # plot check
        '''
        fig, ax = plt.subplots(figsize=(15,10))
        ax.plot(E_phot, mu)
        ax.plot(Ehxr, new_mu)
        ax.set_yscale("log")
        ax.set_xscale("log")
        ax.grid()
        plt.show() 
        '''

        newSpectrum = newSpectrum * np.exp(-new_mu*thickness)
        '''
        fig, ax = plt.subplots(figsize=(15,10))
        ax.plot(Ehxr, newSpectrum)
        ax.set_yscale("log")
        newSpectrum = newSpectrum * np.exp(-new_mu*thickness)
        ax.plot(Ehxr, newSpectrum)
        ax.grid()
        plt.show() 
        '''

    return newSpectrum


def saveSpectra(spectra, energyVector, timestamp):

    if "1" in config.file_rgrs:
        detector = "los1"
    elif "2" in config.file_rgrs:
        detector = "los2"
    elif "3" in config.file_rgrs:
        detector = "los3"
    else:
        detector = "undefined_los"

    savepath = "./Results/" + config.simFolder + "/"

    if not os.path.exists(savepath):
        os.makedirs(savepath)

    for key, value in spectra.items():

        dataSave = np.vstack((energyVector, value)).T

        savename = "Spectrum_" + key + "_" + detector + "_t" + str(timestamp) + "ms.txt"
        np.savetxt(savepath+savename, dataSave, header='Energy [MeV] \t-\t Rate [MeV^-1 s^-1]')







def plotSpectra(spectra, Ehxr):

    

    fig, ax = plt.subplots(figsize=(15,10))

    for key, value in spectra.items():
        ax.plot(Ehxr, value*1e-3, label=key, linewidth = 2.5) # milliseconds

    #ax.set_ylim([1e0, None])
    ax.set_yscale('log')
    ax.set_title("Bremsstrahlung Spectra")
    ax.set_ylabel("Rate (MeV^-1 ms^-1)")
    ax.set_xlabel("Energy (MeV)")
    ax.legend()
    ax.grid()
    plt.show()



def importBackground(Ehxr, factor = 1e-4):

    filename = "./Data/firstWall_background/DT537MW_attenuated_det{}.txt".format(config.detector)

    background = np.loadtxt(filename, unpack = True, skiprows=2)

    E, R = background[0], background[1] # R is already attenuated and det efficiency is already considered
    ebw = E[1:] - E[:-1]
    ebw = np.append(ebw, ebw[-1])
    R = factor*R/ebw                # from Votta's paper: 1e-4
                                    # of residual attenuation

    cs = CubicSpline(E, R)
    R = cs(Ehxr)


    return R