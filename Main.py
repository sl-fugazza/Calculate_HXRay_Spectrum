import numpy as np
import sys

import Include.config as config
config.simFolder = "H26-S10"                            # insert here the simulation ID (aka, the folder name)
config.simPath = "./Data/" + config.simFolder + "/"     
config.file_rgrs = "new_D3_RGRS.txt"                    # insert the Line of Sight filename

import Include.Plasma as plasma
import Include.LoS as los 
import Include.REdist as redist
import Include.functions as func
import Include.CalculateSpectrum as calcSpec

# import matplotlib.pyplot as plt 
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
    Attenuators = {"LiH": ["LiH_attenuation.txt", 1.2] # file + length in metres
                   ,"Steel": ["Steel304_attenuation.txt", 0.04]}
    # initialise los
    myLOS = los.LineOfSight(losFilename=config.file_rgrs, Attenuators = Attenuators)
    # los_params = myLOS.getVoxelList() # extract voxel info
    # myLOS.plotLos("2D") # plot the los (2D or 3D)
    
    #myLOS.addAttenuator("Test", "Steel304_attenuation.txt", 0.01)
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
    neon = func.importSpecies("Ne", 10, "nne1.txt") # in realta ora devo usare tutto il neon e non solo dal file nne1.txt
    
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
    # myPlasma.plotIonDensity("Ne2")
    





    #--------------------------------------------
    # INITIALIZE THE RE DISTRIBUTION
    #--------------------------------------------

    # first, define the RE energy vector
    Ere = np.linspace(0.1, 30.1, 51)

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
    # CALCULATING THE SPECTRUM and PLOTTING
    #--------------------------------------------
    
    # define the hard-x rays energy values
    # Ehxr = np.linspace(np.min(Ere), 15.0, 101) # MeV
    # or: 
    u, p = np.linspace(0.0, 1.0, 101), 2.0
    Emin, Emax = 0.05, 10.01
    Ehxr = Emin + (Emax-Emin)*u**p  # this for concentrating energy point in the low energy range
    # or:
    #Ehxr = np.logspace(-1, +1, 101) # MeV

    # calculation of the spectrum for each ion contribution
    # timestamp, hxr energy vector + los, palsma and re_dist
    spectra = calcSpec.CalculateBremsstrahlungSpectra(t0, Ehxr,
                                    myLOS, myPlasma, myRE) 
    #print(spectra)

    # save spectra
    func.saveSpectra(spectra, Ehxr, t0)
    # plot spectra
    func.plotSpectra(spectra, Ehxr)




    # BACKGROUND
    # il fondo va giu' di 10^4 -- attivazione residua
    # leggere il paper di Votta


    # --------------------------------------------
    # END
    #--------------------------------------------



    

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

if __name__ == '__main__':
    main()






