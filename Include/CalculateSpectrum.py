import config

import numpy as np
import sys
#import matplotlib.pyplot as plt 

from ControlRoom import *


import Plasma as plasma
import LoS as los 
import REdist as redist
import functions as func









# USEFUL FUNCTIONS
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@



def calculateEnergyBCrossSection(Ere,Z,Ehx):
    # calculation of the Bremsstrahlung cross section integrated over all emission angles
    dSdEhx = np.zeros((len(Ere), len(Ehx)))
    for i in range(len(Ere)):
        for j in range(len(Ehx)):
            val = Salvat1992DifferentialCrossSection(Ere[i]*MeV, Z, Ehx[j]*MeV)
            dSdEhx[i,j] = np.float64((val*MeV)/meter**2)
            
    return dSdEhx


def calculateDipoleBCrossSection(Ere, visAngle = 90.0):
    # semplified version of the dipole Bremsstrahlung cross section
    # only co-passing electrons (no gyroangles)
    cosTeta = np.cos(visAngle*np.pi/180.0)

    pDipole = np.zeros(len(Ere))
    for i in range(len(Ere)):
        val = AngularProbability(Ere[i]*MeV, cosTeta)
        pDipole[i] = val/(2.0*np.pi)
    
    return pDipole


'''
def calculateRateFunction(Ere,visAngle,Nre, Ntarg, Ztarg, Ehx):
    # calculation of the so-called RATE FUNCTION

    gamma = 1.0 + (Ere*config.MeV/(config.me*config.c**2))
    beta = np.sqrt(1.0-1.0/gamma**2)
    Vre = beta*config.c
    
    pDipole = calculateDipoleBCrossSection(Ere, visAngle)
    dSdE = calculateEnergyBCrossSection(Ere,Ztarg,Ehx)
    integral = np.trapz(dSdE, x=Ehx)

    Rfunc =  4.0*np.pi* Ntarg*Nre*Vre * integral * pDipole

    return Rfunc
'''


def calculateHXREnergyProbabilityDist(Ere,Z, Ehx):
    # calculation of the so-called "Probability Function"
    dSdE = calculateEnergyBCrossSection(Ere,Z, Ehx)
    
    # total integral over photon energies
    integral = np.trapz(dSdE, x=Ehx, axis = 1)

    
    
    ddp = dSdE/integral[:, None]
    # broadcasting: sto dicendo che ogni riga di dSdE deve essere normalizzata 
    # per il corrispondente valore di integral
    
    return np.abs(ddp), integral


















# PRIMARY FUNCTION
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

def CalculateBremsstrahlungSpectra(timestamp, Ehxr,
                                    LineOfSight, Plasma, REdistribution,
                                    materials = None):

    # .....................................................
    # importing and preparing all inputs and parameters

    # importing the line of sight
    los = LineOfSight.getVoxelList()
    r_voxels = np.array([ v[1] for v in los]) # extracting the r coordinated from each voxel

    # importing coordinates:
    r_plasma, t_plasma = Plasma.getPlasmaCoordinates()
    r_red, t_red, Ere = REdistribution.getREdistCoordinates()

    # cleaning the voxel outside of palsma bounds
    mask = (
    (r_voxels >= np.min(r_plasma)) &
    (r_voxels <= np.max(r_plasma)) &
    (r_voxels >= np.min(r_red)) &
    (r_voxels <= np.max(r_red)) &
    (r_voxels <= config.r_mask)      # r_mask: custom value for eliminating unuseful external voxels
        )   
    los = [ vox for vox in los if mask[vox[0]]==True ] # cleaned los list
    

    # check
    if timestamp > np.max(t_plasma) or timestamp < np.min(t_plasma):
        print("The selected timestamp is out of plasma time window")
        sys.exit()
    if timestamp > np.max(t_red) or timestamp < np.min(t_red):
        print("The selected timestamp is out of the re_dist time window")
        sys.exit()

    
    

    # ..............................................
    # Running for all Ion species

    
    # consider the observation angle fixed (very likely for RGRS at ITER)
    visAng = 90.0 # deg
    # calculation of a preliminary quantity, valid for all ions: the dipole function
    pDipole   = calculateDipoleBCrossSection(Ere, visAng)

    allSpectra = {} # save results here
    
    ionList = Plasma.getIonList()
    for ion in ionList:   # Running for all ions
        
        Znumber = Plasma.getIonZ(ion)  # Z number of the ion
        
        # calculating some preliminar quantities, valid for all voxels
        Sfunc, integral = calculateHXREnergyProbabilityDist(Ere,Znumber, 
                                                      Ehxr)
        # dSdE      = calculateEnergyBCrossSection(Ere, Znumber, Ehxr)
        # integral  = np.trapz(dSdE, x=Ehxr)

        ionSpectrum = np.zeros(len(Ehxr)) # initilaise the spectrum of the selected ion
        for v, voxel in enumerate(los): # running for all voxels    
            # voxels info
            # id_vox = voxel[0]
            r_vox, saf, vol = voxel[1], voxel[2], voxel[3]
            Cfactor = saf*vol # Solid Angle fraction * Volume of the voxel
            # usefull only if we desire to obtain a correct value of the emission angle
            # ux, uy, uz = voxel[4], voxel[5], voxel[6] 

            if v==0 or v%1000 == 0:
                print("Voxel {}/{}".format(v, len(los)))
            
            # Get Ion Density in such voxel
            ionDens =Plasma.getDensValue(ion, r_vox, timestamp)

            # get RE density in such point 
            RE_dens = REdistribution.getREdensValue(r_vox, timestamp)

            # get RE energy distribution in such voxel
            RE_dist = REdistribution.getREdistValue(r_vox, timestamp) 

            # calcualtion of the observation angle
            # to be implemented .... (likely not necessary for RGRS at ITER)

            # calculation of the Rate Function
            gamma = 1.0 + (Ere * config.MeV / (config.me * config.c**2))
            beta  = np.sqrt(1.0 - 1.0/gamma**2)
            Vre   = beta * config.c
            Rfunc = 4.0*np.pi * ionDens * RE_dens * Vre * integral * pDipole
            # adjust rate function with RE dist value in r_vox and C-factor:
            moltFactor   = Rfunc * RE_dist  * Cfactor
            # finally, calculate the spectrum for the specific voxel
            voxelSpectrum = np.sum(Sfunc * moltFactor[:, None], axis=0) # : use of broadcasting

            # summing into the resulting ion spectrum:
            ionSpectrum  += voxelSpectrum

        # finally, apply attenuation
        if materials is not None:
            ionSpectrum = func.attenuateSpectrum(ionSpectrum, Ehxr, materials)

        # add the spectrum for the specific ion
        allSpectra[ion] = ionSpectrum
    
    return allSpectra