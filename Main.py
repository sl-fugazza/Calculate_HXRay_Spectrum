import numpy as np
import sys
# import matplotlib.pyplot as plt 

import Include.config as config
config.simFolder = "H26-S10"
config.simPath = "./Data/" + config.simFolder + "/"
config.file_rgrs = "new_D3_RGRS.txt"

import Include.Plasma as plasma
import Include.LoS as los 
import Include.REdist as redist
import Include.functions as func
import Include.CalculateSpectrum as calcSpec

# from ControlRoom import *


'''
# This code has been developed for calculating Bremsstrahlung spectra from Runaway Electron events at ITER.
# It is divided in four parts: 
#    Defining the lines of Sight of the diagnostic
#    Defining the plasma and species
#    Defining the Runaway Electron distribution
#    Computing the resulting Bremsstrahlung spectra
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

    # select time to be analised 
    t0 = 13.4 # milliseconds

    # position to be analysed (not necessary)
    # r0 = 0.1 # meter






    #--------------------------------------------
    # INITIALIZE THE LINE OF SIGHT
    #--------------------------------------------
    
    myLOS = los.LineOfSight(losFilename=config.file_rgrs)
    # los_params = myLOS.getVoxelList() # extract voxel info
    myLOS.plotLos("2D") # plot the los (2D or 3D)






    #--------------------------------------------
    # INITIALIZE THE PLASMA AND INSERT SPECIES
    #--------------------------------------------

    r_coord, t_coord = func.importCoordinates("r_coordinate.txt", 
                                              "t_coordinate.txt")
   
    hydro = func.importSpecies("H", 1, "nh.txt")
    deut = func.importSpecies("D", 1, "nd.txt")
    trit = func.importSpecies("T", 1, "nt.txt")
    neon1 = func.importSpecies("Ne1", 1, "nne1.txt")
    neon2 = func.importSpecies("Ne2", 2, "nne2.txt")
    
    # initialize plasma
    myPlasma = plasma.Plasma(r_coord, t_coord, 
                             [hydro, deut, trit, neon1, neon2]) 
    
    # add custom species like Tungsten 2 times ionised
    # myPlasma.addSpecies("W74", 74, "nh.txt", 1e-4) # WORST case ever (higly unlikely)
    myPlasma.addSpecies("W74", 74, "nh.txt", 1e-4) # more likely
    # Here, I take a distribution like Hydrogen but with a sclaing factor of 1e-4

    # get the density value
    #densH = myPlasma.getDensValue("H", r0, t0)

    # plot density matrix
    # myPlasma.plotIonDensity("Ne2")
    





    #--------------------------------------------
    # INITIALIZE THE RE DISTRIBUTION
    #--------------------------------------------

    # first, define the RE energy vector
    Ere = np.linspace(0.01, 30.1, 51)
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
    Ehxr = np.linspace(np.min(Ere), 15.0, 101) # MeV
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


# Acciao inossidabile 4 cm + 1.2 m di LiH 
# il fondo si abbassa di un 10^4
    

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

if __name__ == '__main__':
    main()






