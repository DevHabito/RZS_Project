Relational Zero State (RZS) - Observational Validation

This repository contains the observational validation for the Relational Zero State (RZS) cosmological model. The model proposes a latency field Φ with a spectral stability point at α≈1.5 to address the Hubble Tension and early galaxy formation.
🛠 Validation against DESI Data

The primary validation script is located in the /validation folder:

    File: validation/rzs_DESI.py

    Dataset: Processes the BGS_BRIGHT_N_clustering.dat.fits sample from the Dark Energy Spectroscopic Instrument (DESI).

    Methodology: The script converts RA, Dec, and Redshift into 3D Cartesian coordinates to reconstruct the cosmic web's connectivity.

    Spatial Analysis: It uses a cKDTree algorithm to identify galaxy pairings within a physical radius of 6.0 Mpc.

    Key Result: It plots the connectivity probability distribution P(k) against theoretical power laws, demonstrating that observed galaxy clustering aligns with the RZS stability index of α=1.5.

🚀 How to Run

    Ensure you have the required libraries: numpy, matplotlib, astropy, and scipy.

    Place the DESI FITS file in the root directory or update the FILE_NAME path in the script.

    Run the validation:
  
    Bash

  python validation/rzs_DESI.py

  Contact

  Felipe Romero Author of the RZS Framework Manuscript Ref: DARK-D-26-00136 (Physics of the Dark Universe)
