import numpy as np
import sys

import config
import functions as func




class LineOfSight:

    
    def __init__(self, losFilename):
        
        los = np.loadtxt("./Data/linesOfSight/" + losFilename)

        self.x = los[:,0]
        self.y = los[:,1]
        self.z = los[:,2]
        self.Saf = los[:,3]
        self.Vol = los[:,4]
        self.ux = los[:,5]
        self.uy = los[:,6]
        self.uz = los[:,7]

        self.R  = np.sqrt(self.x**2 + self.y**2)
        dR, dZ = self.R-config.R_Maxis, self.z - config.Z_Maxis
        self.r = np.sqrt(dR**2 + dZ**2)

        self.voxelID = np.arange(len(self.r))

    def getVoxelList(self):
        return list(zip(*[self.voxelID,self.r, self.Saf, self.Vol, self.ux, self.uy, self.uz]))
        # this is a list of tuples organized such that each tuple represents a voxel

    def plotLos(self, type):
        
        import matplotlib.pyplot as plt 
        from matplotlib.colors import LogNorm

        
        Rw, Zw = func.importFirstWall()

        print(self.R)

        if type == "2D":
            print("2D plot of the Line of Sight")

            fig, ax = plt.subplots(figsize=(15,10))
            sc = ax.scatter(self.R, self.z, c=self.Saf*self.Vol, cmap="plasma", s=10, norm=LogNorm())
            cbar = fig.colorbar(sc, ax = ax)
            ax.plot(Rw,Zw, linewidth = 3, color = "orange")
            ax.set_xlabel("R (m)")
            ax.set_ylabel("Z (m)")
            ax.grid()
            plt.axis("equal")

            ax.set_facecolor('#000033')
            plt.show()

        elif type == "3D":
            from mpl_toolkits.mplot3d import Axes3D
            print("3D plot of the Line of Sight")

            fig = plt.figure(figsize=(15,15))
            ax = fig.add_subplot(111, projection='3d')
            ax.plot(Rw,np.zeros_like(Rw),Zw, linewidth = 3, color = "orange")
            sc = ax.scatter(self.x, self.y, self.z, c=self.Saf*self.Vol, cmap="plasma", s=10, norm=LogNorm())
            cbar = fig.colorbar(sc, ax = ax)

            ax.set_xlabel("X (m)")
            ax.set_ylabel("Y (m)")
            ax.set_zlabel("Z (m)")
            ax.set_xlim(np.min(self.x), np.max(self.x))
            ax.set_ylim(np.min(self.x)-np.max(self.x), np.max(self.x)-np.min(self.x))
            ax.set_zlim(np.min(self.x)-np.max(self.x), np.max(self.x)-np.min(self.x))
            ax.grid()
            plt.show()


        else:
            print("Please, insert a valid type of plot")
            sys.exit()