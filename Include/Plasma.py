import numpy as np
import sys

# from scipy.interpolate import RegularGridInterpolator as RGI

import functions as func

    
    
class Plasma:

    def __init__(self, r_coord=None, t_coord=None, species=None):
        
        
        if r_coord is not None and t_coord is not None:
            self.r, self.t = r_coord, t_coord
        else:
            self.r, self.t = None, None
        

        self.Species = {}
        if species is None:
            print("Plasma has been initialised empty of species")
        else:
            for spec in species:
            
                if not isinstance(spec[0], str):
                    print("The first element of Species must be a string !")
                    sys.exit()
                if len(spec) != 3:
                    print("Wrong number of element for species !")
                    sys.exit()
                if not isinstance(spec[2], int):
                    print("The last element of Species must be an integer number (Z) !")
                    sys.exit()
                if self.r is not None and self.t is not None:
                    if spec[1].size != self.r.size*self.t.size:
                        print("Something wrong in the density matrix dimensions")
                        sys.exit()
                    
                self.Species[spec[0]] = [spec[1], spec[2]]
            
            print("Species in Plasma:")
            for key, values in self.Species.items():
                print("{} - Z={}".format(key, values[1]))


    # using this method, you can add a new species.
    # moreover, you can add a "test" species cloning another on (es: nh.txt)
    # and using a scaling factor for adjust the density
    def addSpecies(self, newSpeciesID, Z, filename, scalingFactor=1.0):
        newS = func.importSpecies(newSpeciesID, Z, filename)
        self.Species[newS[0]] = [scalingFactor*newS[1], newS[2]]

        print("New Species added:")
        print("{} - Z={}".format(newS[0], newS[2]))




    def getIonList(self):
        return self.Species.keys()
    
    def getIonDensity(self, ionName):
        print("Ion: "+ionName + " Density: ")
        print( self.Species[ionName][0] )
        return self.Species[ionName][0]
    
    def getIonZ(self, ionName):
        print("Ion: "+ionName + " Z: " + str(self.Species[ionName][1]))
        return self.Species[ionName][1]
    
    def getPlasmaCoordinates(self):
        return self.r, self.t
    




    def getDensValue(self, ionName, r0, t0):
        
        density = self.Species[ionName][0]
        
        # nearest neighbour method
        ir = np.argmin(np.abs(self.r - r0))
        it = np.argmin(np.abs(self.t - t0))

        densVal = density[it,ir] # [it, ir] because the matrix is transposed

        # interpolation method
        #interp = RGI( (self.r,self.t), density.T, method='linear')
        #densVal = interp((r0, t0))

        return densVal



    def plotIonDensity(self, ionName):
        
        import matplotlib.pyplot as plt 
        #from matplotlib.colors import LogNorm

        density = self.Species[ionName][0]
        

        fig, ax = plt.subplots(figsize=(7,7))
        c = plt.contourf(self.r, self.t, density, levels=100, cmap = 'plasma') 
        # c = plt.contourf(self.r, self.t, density, levels=100, cmap = 'plasma', norm=LogNorm())
        fig.colorbar(c, ax=ax)
        ax.grid()

        plt.show()