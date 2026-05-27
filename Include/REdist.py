import numpy as np
import sys

from scipy.interpolate import RegularGridInterpolator as RGI

#import config 


import matplotlib.pyplot as plt 
#from matplotlib.colors import LogNorm


class REdist:



    def __init__(self, r, t, Ere, nre):

        self.r_coord = r
        self.t_coord = t
        self.Ere = Ere

        self.nre = nre
        self.normDist = np.ones( (len(r), len(t), len(Ere)) ) /(Ere[-1]-Ere[0])  # initialised as uniform dist

    def setDistType(self, type, parameter):
        
        # other types can be implemented ...
        # actually, not only co-passing monopitch distribution can be used ... 
        
        if type == "SimpleExponential":
            
            if len(parameter) != 1:
                print("Please, give a single value list [param] for SimpleExponential distribution")
                sys.exit()
            else:
                parameter = parameter[0]

            for k in range(len(self.Ere)):
                self.normDist[:,:,k] = 1/parameter * np.exp(-self.Ere[k]/parameter)

        elif type == "Exponential":

            if parameter.size != self.nre.size:
                print("T-matrix and RE density matrix must have same dimensions")
                sys.exit()

            for i in range(len(self.r_coord)):
                for j in range(len(self.t_coord)):
                    for k in range(len(self.Ere)):
                        self.normDist[i,j,k] = 1.0/parameter[i,j] * np.exp(-self.Ere[k]/parameter[i,j])
            
            
        elif type == "Custom":
            if parameter.size != self.normDist.size:
                print("Please, give in input a tensor of the same size of the RE distribution")
                sys.exit()
            self.normDist = parameter
        else:
            print("Please, give a proper type of RE distribution")



    def getREdistCoordinates(self):
        return self.r_coord, self.t_coord, self.Ere
    

    def getREdensValue(self, r_point, t_point):

        if r_point > np.max(self.r_coord) or r_point < np.min(self.r_coord):
            print("the r point selected is too big or too small")
            sys.exit()
        if t_point > np.max(self.t_coord) or t_point < np.min(self.t_coord):
            print("the t point selected is too big or too small")
            sys.exit()
        
        interp = RGI( (self.r_coord, self.t_coord), self.nre.T, method='linear')

        return interp((r_point, t_point))
    
    def getREdistValue(self, r_point, t_point):

        if r_point > np.max(self.r_coord) or r_point < np.min(self.r_coord):
            print("the selected r-point is too big or too small")
            sys.exit()
        if t_point > np.max(self.t_coord) or t_point < np.min(self.t_coord):
            print("the selected timestamp is too big or too small")
            sys.exit()

        # nearest neighbour
        ir = np.argmin(np.abs(self.r_coord - r_point))
        it = np.argmin(np.abs(self.t_coord - t_point))

        mono_dist = self.normDist[ir,it,:]

        return mono_dist



    def plotREdensity(self):

        fig, ax = plt.subplots(figsize=(7,7))
        
        c = plt.contourf(self.r_coord, self.t_coord, self.nre, levels=100, cmap = 'plasma') 

        fig.colorbar(c, ax=ax)
        ax.grid()

        plt.show()


    def plotRE_energyDist(self, r_point, t_point):

        ir = np.argmin(np.abs(self.r_coord - r_point))
        it = np.argmin(np.abs(self.t_coord - t_point))

        energy_dist = self.normDist[ir,it,:]

        dens = self.getREdensValue(r_point, t_point)

        final_dist = energy_dist * dens



        fig, ax = plt.subplots(figsize=(7,7))

        ax.plot(self.Ere, final_dist, linewidth=2) 
        
        ax.grid()

        plt.show()


