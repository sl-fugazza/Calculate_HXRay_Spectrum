# Calculate_HXRay_Spectrum
This code has been developed for calculating Bremsstrahlung spectra (hard X-ray energy range) from Runaway Electron events at ITER, collected by the RGRS gamma diagnostic.


## Data folder
Here, you can find the first wall of ITER file. You can update it with a better design.
In "linesOfSight" you can find the RGRS field of view inside the plasma. You can update them with improved geometries.
Then you can find simulation outputs of the DREAM code inside corresponding folders. For example, "H26-S10" refers to a specific simulation (S10) in a specific experimental configuration at ITER in a Hydrogen plasma (H26). You can insert all DREAM simulation you want.

## Results folder
Here, you can find the files of the spectra calculated by the code. They are divided based on the specific DREAM simulation (different subfolders) and the ion species (different files).

## Include folder
Here, you find the python files of class and functions of the code. 
In "config.py" you can set some input parameters, like "r_mask" (r-coordinate cut-off: for value of r bigger than that, voxels are skipped).
In "functions.py" there are some basic functions for performing various simple tasks. 
In "LoS.py" the class of the RGRS Line of Sight is implemented. Similarly, the plasma species and the runway electron distribution classes are implemented in "Plasma.py" and "REdist.py", respectively.
Finally, in "CalculateSpectrum.py", the function for the calculation of the bremsstrahlung spectra is implemented. The task is performed for all ion species, and for each voxel of the Line of Sight. In this part of the code, the Genesis libraries are used (ControlRoom).
The photon emission angle is set equal to 90°, in order to simplify the model. This should still be accurate: the RGRS line of sight are well-collimated and radial. 
## Main File
Here, you should initialize input parameters (e.g., the DREAM simulation outputs folder, the time of the discharge, the line of sight file).