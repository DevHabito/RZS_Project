import mne
import numpy as np
from antropy import lziv_complexity

# 1. Carregar o arquivo .fif que você baixou
file_path = 'sub-2218A_ses-0001_task-attnmod_run-01_meg.fif'
raw = mne.io.read_raw_fif(file_path, preload=True)

# 2. Selecionar apenas os sensores de MEG e filtrar (0.5 - 45Hz)
raw.pick_types(meg=True).filter(0.5, 45)

# 3. Pegar os dados de um sensor central (ex: sensor índice 100)
data = raw.get_data(picks=[100])[0]

# 4. Binarização (Transformar ondas em 0s e 1s para o algoritmo LZ)
# Usamos a média do sinal como limiar
binary_signal = data > np.mean(data)

# 5. Calcular a Complexidade Lempel-Ziv (LZc)
lzc_value = lziv_complexity(binary_signal, normalize=True)

print(f"O valor de Entropia (LZc) do sinal é: {lzc_value}")