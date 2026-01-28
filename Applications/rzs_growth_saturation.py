import numpy as np
import matplotlib.pyplot as plt

# ============================
# General settings
# ============================
np.random.seed(42)

n_modes = 512
timesteps = 500

alphas = [1.2, 1.4, 1.5, 1.6, 1.8]

# critical density (ceiling scale)
Ec = 1.0

# base growth rate
gamma = 0.08

# ============================
# RZS field evolution
# ============================
def evolve_field(alpha):
    field = np.random.normal(0, 0.05, n_modes)
    energy_history = []

    for t in range(timesteps):

        # Spectral space
        spectrum = np.fft.fft(field)
        power = np.abs(spectrum)**2

        # ----------------------------
        # GROWTH TERM (active)
        # grows at low densities
        # saturates naturally
        # ----------------------------
        growth = 1.0 + gamma * (power / Ec) * np.exp(-power / Ec)

        # ----------------------------
        # RZS STABILITY TERM
        # rigidity controlled by alpha
        # ----------------------------
        stability = 1.0 / (1.0 + (power / Ec)**alpha)

        # Full spectral evolution
        spectrum = spectrum * growth * stability

        # Return to real space
        field = np.real(np.fft.ifft(spectrum))

        total_energy = np.sum(field**2)
        energy_history.append(total_energy)

        # Numerical instability = physical collapse
        if not np.isfinite(total_energy) or total_energy > 1e6:
            break

    return np.array(energy_history)

# ============================
# Execution
# ============================
plt.figure(figsize=(10,6))

for alpha in alphas:
    energy = evolve_field(alpha)
    plt.plot(energy, label=f"α = {alpha}")

plt.axhline(1e6, linestyle="--", color="black", alpha=0.4, label="Instability")
plt.yscale("log")
plt.xlabel("Time")
plt.ylabel("Total Energy (log)")
plt.title("Growth, Saturation and Emergent Energy Ceiling (RZS)")
plt.legend()
plt.tight_layout()
plt.show()