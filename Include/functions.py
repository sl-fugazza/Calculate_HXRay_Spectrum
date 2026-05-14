import config

import numpy as np
import sys, os
import matplotlib.pyplot as plt 



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

    ax.set_ylim([1e0, None])
    ax.set_yscale('log')
    ax.set_title("Bremsstrahlung Spectra")
    ax.set_ylabel("Rate (MeV^-1 ms^-1)")
    ax.set_xlabel("Energy (MeV)")
    ax.legend()
    ax.grid()
    plt.show()