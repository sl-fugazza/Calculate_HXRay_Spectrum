import numpy as np
import sys

import Include.config as config
config.simFolder = "DT-M5"                    # insert here the simulation ID (aka, the folder name)
config.simPath = "./Data/DREAM_Simulations/" + config.simFolder + "/"    
config.detector = 2
config.file_rgrs = "new_D{}_RGRS.txt".format(config.detector)  # insert the Line of Sight filename

import Include.Plasma as plasma
import Include.LoS as los 
import Include.REdist as redist
import Include.functions as func
import Include.CalculateSpectrum as calcSpec

import matplotlib.pyplot as plt 
# from ControlRoom import *


'''
# This code has been developed for calculating Bremsstrahlung spectra from Runaway Electron events at ITER.
# It is divided in four parts: 
#    1) Definition ofthe lines of Sight of the diagnostic
#    2) Definition of the plasma and species
#    3) Definition of the Runaway Electron distribution
#    4) Calculation of the resulting Bremsstrahlung spectra
# Eventually, the spectra are saved and plotted
#
# This code relies on the Genesis (Controlroom) libraries. Please, install them before running this code.
# Python2 is required for using genesis code.
'''

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

def main():

    #--------------------------------------------
    # INPUT VALUES 
    #--------------------------------------------

    # select the time to be analised 
    t0 = 13.4 # milliseconds

    # position to be analysed (only for checking or analysis)
    # r0 = 0.1 # meter






    #--------------------------------------------
    # INITIALIZE THE LINE OF SIGHT
    #--------------------------------------------
    
    # define attenuating materials
    Attenuators = {"LiH": ["LiH_attenuation.txt", 1.2] 
                   ,"Steel": ["Steel304_attenuation.txt", 0.04]}
    # file + length in metres

    # initialise los
    myLOS = los.LineOfSight(losFilename=config.file_rgrs, 
                            Attenuators = Attenuators)
    # los_params = myLOS.getVoxelList() # extract voxel info

    # myLOS.plotLos("2D") # plot the los (2D or 3D)
    
    #myLOS.addAttenuator("Test", 
    # "Steel304_attenuation.txt", 0.01)
    myLOS.printAttenuators()







    #--------------------------------------------
    # INITIALIZE THE PLASMA AND INSERT SPECIES
    #--------------------------------------------

    r_coord, t_coord = func.importCoordinates("r_coordinate.txt", 
                                              "t_coordinate.txt")
    # studiare il concetto di Carica efficace in funzione dell'energia del RE
    hydro = func.importSpecies("H", 1, "nh.txt") # dovrei aggiungerci anche il neutro
    deut = func.importSpecies("D", 1, "nd.txt") # in teoria anche il neutro
    trit = func.importSpecies("T", 1, "nt.txt") # dovrei aggiunger eanche il neutro
    neon = func.importSpecies("Ne", 10, "nne.txt") # in realta ora devo usare tutto il neon e non solo dal file nne1.txt
    
    # initialize plasma
    myPlasma = plasma.Plasma(r_coord, t_coord, 
                             [hydro, deut, trit, neon]) 
    
    # add custom species like W 
    myPlasma.addSpecies("W", 74, "nh.txt", 1e-4)
    # Here, I take a distribution like Hydrogen 
    # but with a scaling factor of 1e-4 / 1e-5

    # get the density value
    # densH = myPlasma.getDensValue("H", r0, t0)

    # plot density matrix
    # myPlasma.plotIonDensity("Ne")
    





    #--------------------------------------------
    # INITIALIZE THE RE DISTRIBUTION             
    #--------------------------------------------

    # first, define the RE energy vector
    #u, p = np.linspace(0.0, 1.0, 401), 2.0
    #Emin, Emax = 1.0, 31.0
    #Ere = Emin + (Emax-Emin)*u**p
    Ere = np.linspace(.1, 30.1, 401)
    
    # and import the RE density 
    nre = func.importREdensity("nRE.txt")
    
    # initialised the RE distribution
    myRE = redist.REdist(r_coord, t_coord, Ere, nre) 
    # It is initialised as a uniform dist

    # Setting a negative exponential distribution
    Tvalue = 5.0 # MeV
    myRE.setDistType("SimpleExponential", [Tvalue])
    # SimpleExponential: 
    # a negative exp distribution equal in all points and times of the plasma
    # Other types implemented: Exponential, Custom

    # get the density value in r0, t0
    # reDens = myRE.getREdensValue(r0, t0)
    # get the normnalised RE distribution value in r0, t0
    # reDistValue = myRE.getREdistValue(r0, t0)

    # plot the RE density and/or the RE energy distribution
    # myRE.plotREdensity()
    # myRE.plotRE_energyDist(r0, t0)








    #--------------------------------------------
    # CALCULATING THE SPECTRUM
    #--------------------------------------------
    
    # define the hard-x rays energy values
    # Ehxr = np.linspace(np.min(Ere), 15.0, 101) # MeV
    # or: 
    u, p = np.linspace(0.0, 1.0, 401), 2.0
    Emin, Emax = 0.1, 10.1
    Ehxr = Emin + (Emax-Emin)*u**p  # this for concentrating energy point in the low energy range
    # or:
    #Ehxr = np.logspace(-1, +1, 101) # MeV

    # calculation of the spectrum for each ion contribution
    # timestamp, hxr energy vector + los, palsma and re_dist
    spectra = calcSpec.CalculateBremsstrahlungSpectra(t0, Ehxr,
                                    myLOS, myPlasma, myRE,
                                    Efficiency=0.8) # we suppose constant detector efficiency
    #print(spectra)

    # save spectra
    func.saveSpectra(spectra, Ehxr, t0)
    # plot spectra
    # func.plotSpectra(spectra, Ehxr)








    # --------------------------------------------
    # BACKGROUND + FINAL PLOT
    #--------------------------------------------

    backG = func.importBackground(Ehxr, factor = 1e-4)

    TotEmission = backG


    fig, ax = plt.subplots(figsize=(15,5))

    ax.plot(Ehxr, backG*1e-3, label="BG", linewidth = 2.5) # milliseconds

    for key, value in spectra.items():
        TotEmission += value
        ax.plot(Ehxr, value*1e-3, label=key, linewidth = 2.5) # milliseconds

    # ax.plot(Ehxr, TotEmission*1e-3, label="Total" , linewidth = 3.5) # milliseconds

    ax.set_yscale('log')
    ax.set_title("Bremsstrahlung and background Spectra")
    ax.set_ylabel("Rate (MeV^-1 ms^-1)")
    ax.set_xlabel("Energy (MeV)")
    ax.legend()
    ax.grid()

    plt.show()








    # --------------------------------------------
    # END
    #--------------------------------------------



    

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

if __name__ == '__main__':
    main()






