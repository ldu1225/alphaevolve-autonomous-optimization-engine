def compute_fir_response(x_signal):
    n = len(x_signal)
    y_signal = np.zeros(n, dtype=int)
    # EVOLVE-BLOCK-START
    for i in range(7, n):
        # Exploiting symmetry: pre-add symmetric pairs to halve the arithmetic complexity
        s0 = x_signal[i] + x_signal[i-7]
        s1 = x_signal[i-1] + x_signal[i-6]
        s2 = x_signal[i-2] + x_signal[i-5]
        s3 = x_signal[i-3] + x_signal[i-4]

        # Shift-based multiplication to avoid costly hardware multipliers (coefficients: 1, 2, 4, 8)
        y_signal[i] = s0 + (s1 << 1) + (s2 << 2) + (s3 << 3)
    # EVOLVE-BLOCK-END
    return y_signal