def compute_fir_response(x_signal):
    n = len(x_signal)
    y_signal = np.zeros(n, dtype=int)
    # EVOLVE-BLOCK-START
    for i in range(7, n):
        # Symmetric inputs pairing to exploit filter symmetry and reduce operation count
        s0 = x_signal[i] + x_signal[i-7]
        s1 = x_signal[i-1] + x_signal[i-6]
        s2 = x_signal[i-2] + x_signal[i-5]
        s3 = x_signal[i-3] + x_signal[i-4]

        # Efficient bitwise left shifts instead of expensive hardware multipliers
        t1 = s1 << 1
        t2 = s2 << 2
        t3 = s3 << 3

        # Balanced adder tree structure to minimize signal propagation delay (3 levels deep)
        stage1_0 = s0 + t1
        stage1_1 = t2 + t3
        y_signal[i] = stage1_0 + stage1_1
    # EVOLVE-BLOCK-END
    return y_signal