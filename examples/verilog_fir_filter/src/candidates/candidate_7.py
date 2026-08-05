def compute_fir_response(x_signal):
    n = len(x_signal)
    y_signal = np.zeros(n, dtype=int)
    # EVOLVE-BLOCK-START
    # Initialize shift register variables to represent hardware delay lines (D-FFs)
    x0, x1, x2, x3, x4, x5, x6 = (
        x_signal[0], x_signal[1], x_signal[2], x_signal[3], x_signal[4], x_signal[5], x_signal[6]
    )

    for i in range(7, n):
        x7 = x_signal[i]

        # Exploit symmetric filter coefficients to pre-add paired taps
        s0 = x7 + x0
        s1 = x6 + x1
        s2 = x5 + x2
        s3 = x4 + x3

        # Factored adder tree to reduce adder bit-width (from 20-bit to 18-bit),
        # minimizing gate area, power consumption, and critical path propagation delay.
        sum_01 = (s1 << 1) + s0
        sum_23 = ((s3 << 1) + s2) << 2
        y_signal[i] = sum_01 + sum_23

        # Shift the hardware register pipeline
        x0, x1, x2, x3, x4, x5, x6 = x1, x2, x3, x4, x5, x6, x7
    # EVOLVE-BLOCK-END
    return y_signal