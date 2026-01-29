import numpy as np
import matplotlib.pyplot as plt

# ============================
# Parâmetros do experimento
# ============================
np.random.seed(42)

n_modes = 512
timesteps = 300
energy_injection = np.linspace(0.1, 5.0, timesteps)

alphas = [1.2, 1.4, 1.5, 1.6, 1.8]

# ============================
# Função de evolução RZS
# ============================
def evolve_field(alpha):
    field = np.random.normal(0, 0.1, n_modes)
    energy_history = []

    for E in energy_injection:
        # densidade espectral
        spectrum = np.fft.fft(field)
        power = np.abs(spectrum)**2

        # injeção de energia
        power *= (1 + E)

        # termo de estabilidade RZS
        stability = np.exp(-alpha * power / np.max(power))

        # evolução
        spectrum = spectrum * stability

        # retorno ao espaço real
        field = np.real(np.fft.ifft(spectrum))

        # energia total
        total_energy = np.sum(field**2)
        energy_history.append(total_energy)

        # colapso numérico = instabilidade física
        if not np.isfinite(total_energy) or total_energy > 1e6:
            break

    return energy_history

# ============================
# Execução
# ============================
plt.figure(figsize=(10,6))

for alpha in alphas:
    energy = evolve_field(alpha)
    plt.plot(energy, label=f"α = {alpha}")

plt.axhline(1e6, linestyle="--", color="black", alpha=0.5, label="Instabilidade")

plt.yscale("log")
plt.xlabel("Tempo")
plt.ylabel("Energia Total (log)")
plt.title("Teto de Energia e Estabilidade Espectral (RZS)")
plt.legend()
plt.tight_layout()
plt.show()
