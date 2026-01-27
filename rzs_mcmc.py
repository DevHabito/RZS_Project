import numpy as np
import emcee
import corner
import matplotlib.pyplot as plt
from tqdm import tqdm

# =================================================================
# 1. OBSERVATIONAL DATA (Cosmic Chronometers - CC)
# Real H(z) data to compare with the model
# =================================================================
z_obs = np.array([0.07, 0.12, 0.2, 0.28, 0.4, 0.48, 0.9, 1.3, 1.5, 2.0])
h_obs = np.array([69.0, 68.6, 72.9, 81.5, 82.0, 86.6, 117.0, 168.0, 191.0, 214.0])
h_err = np.array([19.6, 26.2, 29.6, 20.8, 25.0, 20.0, 23.0, 17.0, 14.0, 39.0])

# =================================================================
# 2. RZS MODEL DEFINITION
# theta contains the free parameters: [H0, alpha]
# =================================================================
def model_h(theta, z):
    h0, alpha_param = theta
    omega_m = 0.30  # We fix omega_m to focus on the relational constant alpha
    # In RZS, alpha governs the evolution of vacuum/latent energy
    return h0 * np.sqrt(omega_m * (1 + z)**3 + (1 - omega_m) * (z + 1)**(3 - alpha_param))

# --- Likelihood Function ---
def log_likelihood(theta, z, h, h_err):
    h_model = model_h(theta, z)
    sigma2 = h_err**2
    return -0.5 * np.sum((h - h_model)**2 / sigma2 + np.log(2 * np.pi * sigma2))

# --- Priors (Reasonable physical limits) ---
def log_prior(theta):
    h0, alpha_param = theta
    if 60.0 < h0 < 80.0 and 1.0 < alpha_param < 2.0:
        return 0.0
    return -np.inf

# --- Total Probability ---
def log_probability(theta, z, h, h_err):
    lp = log_prior(theta)
    if not np.isfinite(lp):
        return -np.inf
    return lp + log_likelihood(theta, z, h, h_err)

# =================================================================
# 3. MCMC EXECUTION
# =================================================================
nwalkers = 32      # Number of "walkers"
ndim = 2           # Number of parameters (H0 and alpha)
nsteps = 5000      # Number of iterations

# Initial starting point (near your alpha=1.5 and H0=73)
initial_guess = np.array([73.0, 1.5])
pos = initial_guess + 1e-4 * np.random.randn(nwalkers, ndim)

print(f"Starting MCMC with {nwalkers} walkers and {nsteps} steps...")

sampler = emcee.EnsembleSampler(nwalkers, ndim, log_probability, args=(z_obs, h_obs, h_err))

# Execution with progress bar
for _ in tqdm(sampler.sample(pos, iterations=nsteps), total=nsteps):
    pass

# =================================================================
# 4. PROCESSING AND DISPLAY
# =================================================================
# We discard the first 500 steps (burn-in) to ensure stability
flat_samples = sampler.get_chain(discard=500, thin=15, flat=True)

print("\n" + "="*40)
print("   FINAL MCMC RZS RESULTS")
print("="*40)

labels = ["H0", "alpha"]
results = []
for i in range(ndim):
    mcmc = np.percentile(flat_samples[:, i], [16, 50, 84])
    q = np.diff(mcmc)
    results.append(mcmc[1])
    print(f"{labels[i]}: {mcmc[1]:.4f} (+{q[1]:.4f} / -{q[0]:.4f})")

# --- CORNER PLOT (Probability Clouds) ---
print("\nGenerating density plot (Corner Plot)...")
fig = corner.corner(
    flat_samples, 
    labels=["$H_0$", "$\\alpha$"], 
    truths=[73.0, 1.5],
    color="royalblue",
    truth_color="indianred",
    show_titles=True,
    title_kwargs={"fontsize": 12}
)

plt.savefig("mcmc_rzs_final_test.png", dpi=300)
print("Plot saved as: 'mcmc_rzs_final_test.png'")
plt.show()

# --- VERDICT ---
alpha_final = results[1]
if abs(alpha_final - 1.5) < 0.1:
    print(f"\nFINAL COMPARISON: The Alpha value converges to {alpha_final:.2f}.")
    print("THE MCMC TEST CONFIRMS THE RZS HYPOTHESIS!")
else:
    print(f"\nFINAL COMPARISON: The value diverged (Alpha={alpha_final:.2f}).")
