import mne
import numpy as np
import networkx as nx
from scipy.stats import linregress
from antropy import lziv_complexity

# =========================================================
# 1. Load MEG data
# =========================================================
raw = mne.io.read_raw_fif(
    'sub-2218A_ses-0001_task-attnmod_run-01_meg.fif',
    preload=True
)

# Use only magnetometers and apply band-pass filter
raw = raw.copy().pick_types(meg='mag')
raw.filter(0.5, 45)

sfreq = raw.info['sfreq']
data = raw.get_data()  # shape: (n_channels, n_times)

# Remove linear trends
data = mne.filter.detrend(data, axis=1)

# =========================================================
# 2. Window parameters
# =========================================================
window_sec = 5.0
window_samples = int(window_sec * sfreq)

lzc_values = []
alpha_values = []

# =========================================================
# 3. Windowed analysis
# =========================================================
for start in range(0, data.shape[1] - window_samples, window_samples):

    segment = data[:, start:start + window_samples]

    # -------------------------------
    # LZ complexity (single channel)
    # -------------------------------
    channel_signal = segment[0]  # pick first magnetometer
    binary_signal = channel_signal > np.median(channel_signal)
    lzc = lziv_complexity(binary_signal.astype(int), normalize=True)
    lzc_values.append(lzc)

    # -------------------------------
    # Functional connectivity
    # -------------------------------
    corr_matrix = np.corrcoef(segment)

    # Threshold by density (top 5%)
    threshold = np.percentile(np.abs(corr_matrix), 95)
    adj_matrix = (np.abs(corr_matrix) > threshold).astype(int)
    np.fill_diagonal(adj_matrix, 0)

    G = nx.from_numpy_array(adj_matrix)

    degrees = np.array([d for _, d in G.degree() if d > 0])

    if len(degrees) < 5:
        continue  # avoid unstable fits

    k, counts = np.unique(degrees, return_counts=True)
    pk = counts / counts.sum()

    log_k = np.log10(k)
    log_pk = np.log10(pk)

    slope, intercept, r_value, p_value, std_err = linregress(log_k, log_pk)
    alpha = -slope

    alpha_values.append(alpha)

# =========================================================
# 4. Results
# =========================================================
lzc_values = np.array(lzc_values)
alpha_values = np.array(alpha_values)

print("\n--- WINDOWED RESULTS ---")
print(f"Mean LZ complexity : {lzc_values.mean():.3f} ± {lzc_values.std():.3f}")
print(f"Mean alpha (geometry): {alpha_values.mean():.3f} ± {alpha_values.std():.3f}")

# Correlation between LZc and alpha
min_len = min(len(lzc_values), len(alpha_values))
corr = np.corrcoef(lzc_values[:min_len], alpha_values[:min_len])[0, 1]

print(f"LZc–alpha correlation: {corr:.3f}")
print("-------------------------")
