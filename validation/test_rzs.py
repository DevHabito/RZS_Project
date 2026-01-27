import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits  # You already have this
from scipy.spatial import cKDTree
import os

FILE_NAME = 'BGS_BRIGHT_N_clustering.dat.fits'
N_AMOSTRA = 25000 
RAIO_MPC = 6.0 

def comparar_alphas_manual():
    if not os.path.exists(FILE_NAME):
        print("FILE NOT FOUND!")
        return

    print("1/4: Loading data...")
    with fits.open(FILE_NAME) as hdul:
        data = hdul[1].data
        indices = np.random.choice(len(data), N_AMOSTRA, replace=False)
        ra = np.radians(data['RA'][indices])
        dec = np.radians(data['DEC'][indices])
        z = data['Z'][indices]

    print("2/4: Converting to 3D (Hubble approximation)...")
    # Simplified Hubble constant to convert redshift to distance (Mpc)
    c = 299792.458  # Speed of light km/s
    H0 = 70.0       # km/s/Mpc
    distancia = (c * z) / H0

    # Conversion from spherical to 3D Cartesian coordinates
    x = distancia * np.cos(dec) * np.cos(ra)
    y = distancia * np.cos(dec) * np.sin(ra)
    z_coord = distancia * np.sin(dec)
    coords = np.column_stack((x, y, z_coord))

    print("3/4: Computing real connectivity...")
    tree = cKDTree(coords)
    pares = tree.query_pairs(r=RAIO_MPC)

    graus = np.zeros(N_AMOSTRA)
    for i, j in pares:
        graus[i] += 1
        graus[j] += 1

    graus_filtrados = graus[graus > 0]

    print("4/4: Generating normalized P(k) plot...")
    bins = np.arange(1, graus_filtrados.max() + 2)
    counts, edges = np.histogram(graus_filtrados, bins=bins)
    
    Pk = counts / counts.sum()
    k_centers = edges[:-1]
    mask = Pk > 0

    plt.figure(figsize=(12, 7))
    plt.scatter(
        k_centers[mask], 
        Pk[mask], 
        color='black', 
        s=100, 
        label='DESI Data (Observed)'
    )

    x_teorico = np.logspace(0, np.log10(k_centers.max()), 100)
    
    def power_law(a):
        return x_teorico**(-a) * (Pk[mask][0] * (k_centers[mask][0]**a))

    plt.plot(x_teorico, power_law(1.1), 'g--', alpha=0.5, label='Alpha 1.1')
    plt.plot(x_teorico, power_law(1.5), 'r-', linewidth=3, label='Alpha 1.5 (RZS)')
    plt.plot(x_teorico, power_law(2.0), 'b--', alpha=0.5, label='Alpha 2.0')

    plt.xscale('log')
    plt.yscale('log')
    plt.xlabel('k (Number of real connections)')
    plt.ylabel('P(k) Probability')
    plt.title('Scientific Validation: DESI Galaxy Network')
    plt.grid(True, which="both", alpha=0.1)
    plt.legend()
    plt.show()

comparar_alphas_manual()
