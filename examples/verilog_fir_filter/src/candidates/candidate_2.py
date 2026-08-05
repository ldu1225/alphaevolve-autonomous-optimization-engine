def compute_fir_response(x_signal):
    n = len(x_signal)
    y_signal = np.zeros(n, dtype=int)
    # EVOLVE-BLOCK-START
    for i in range(7, n):
        # Exploit symmetric filter coefficients to pre-add paired taps
        s0 = x_signal[i] + x_signal[i-7]
        s1 = x_signal[i-1] + x_signal[i-6]
        s2 = x_signal[i-2] + x_signal[i-5]
        s3 = x_signal[i-3] + x_signal[i-4]

        # Use zero-cost bitwise shifts instead of area-heavy multipliers
        t0 = s0
        t1 = s1 << 1
        t2 = s2 << 2
        t3 = s3 << 3

        # Balanced adder tree to minimize critical path propagation delay
        sum_01 = t0 + t1
        sum_23 = t2 + t3
        y_signal[i] = sum_01 + sum_23
    # EVOLVE-BLOCK-END
    return y_signal