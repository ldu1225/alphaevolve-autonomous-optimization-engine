def compute_fir_response(x_signal):
    n = len(x_signal)
    y_signal = np.zeros(n, dtype=int)
    # EVOLVE-BLOCK-START
    for i in range(7, n):
        y_signal[i] = (x_signal[i] * 1) + (x_signal[i-1] * 2) + (x_signal[i-2] * 4) + (x_signal[i-3] * 8) + (x_signal[i-4] * 8) + (x_signal[i-5] * 4) + (x_signal[i-6] * 2) + (x_signal[i-7] * 1)
    # EVOLVE-BLOCK-END
    return y_signal