import numpy as np
import matplotlib.pyplot as plt

# ============================
# Experiment parameters
# ============================
np.random.seed(42)

n_modes = 512
timesteps = 300
energy_injection = np.linspace(0.1, 5.0, timesteps)

alphas = [1.2, 1.4, 1.5, 1.6, 1.8]

# ============================
# RZS evolution function
# ============================
def evolve_field(alpha):
    field = np.random.normal(0, 0.1, n_modes)
    energy_history = []

    for E in energy_injection:
        # spectral density
        spectrum = np.fft.fft(field)
        power = np.abs(spectrum)**2

        # energy injection
        power *= (1 + E)

        # RZS stability term
        stability = np.exp(-alpha * power / np.max(power))

        # evolution
        spectrum = spectrum * stability

        # return to real space
        field = np.real(np.fft.ifft(spectrum))

        # total energy
        total_energy = np.sum(field**2)
        energy_history.append(total_energy)

        # numerical collapse = physical instability
        if not np.isfinite(total_energy) or total_energy > 1e6:
            break

    return energy_history

# ============================
# Execution
# ============================
plt.figure(figsize=(10,6))

for alpha in alphas:
    energy = evolve_field(alpha)
    plt.plot(energy, label=f"α = {alpha}")

plt.axhline(1e6, linestyle="--", color="black", alpha=0.5, label="Instability")

plt.yscale("log")
plt.xlabel("Time")
plt.ylabel("Total Energy (log)")
plt.title("Energy Ceiling and Spectral Stability (RZS)")
plt.legend()
plt.tight_layout()
plt.show()