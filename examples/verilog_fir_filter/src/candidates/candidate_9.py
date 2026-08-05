def compute_fir_response(x_signal):
    n = len(x_signal)
    y_signal = np.zeros(n, dtype=int)
    # EVOLVE-BLOCK-START
    for i in range(7, n):
        # Leverage symmetry to reduce multipliers and adders
        sym0 = x_signal[i] + x_signal[i-7]
        sym1 = x_signal[i-1] + x_signal[i-6]
        sym2 = x_signal[i-2] + x_signal[i-5]
        sym3 = x_signal[i-3] + x_signal[i-4]

        # Use shift operations instead of expensive multiplications (Power-of-2 coefficients)
        s0 = sym0
        s1 = sym1 << 1
        s2 = sym2 << 2
        s3 = sym3 << 3

        # Balanced tree adder structure to minimize critical path delay
        sum_01 = s0 + s1
        sum_23 = s2 + s3
        y_signal[i] = sum_01 + sum_23
    # EVOLVE-BLOCK-END
    return y_signal