def compute_fir_response(x_signal):
    n = len(x_signal)
    y_signal = np.zeros(n, dtype=int)
    # EVOLVE-BLOCK-START
    for i in range(7, n):
        # Stage 1: Symmetric input pairs addition to exploit filter symmetry
        s07 = x_signal[i] + x_signal[i-7]
        s16 = x_signal[i-1] + x_signal[i-6]
        s25 = x_signal[i-2] + x_signal[i-5]
        s34 = x_signal[i-3] + x_signal[i-4]

        # Stage 2: Scaling via bitwise left shifts (zero-cost hardware routing)
        t0 = s07
        t1 = s16 << 1
        t2 = s25 << 2
        t3 = s34 << 3

        # Stage 3: Balanced binary adder tree to minimize critical path propagation delay
        sum_01 = t0 + t1
        sum_23 = t2 + t3

        # Stage 4: Final pipeline stage accumulation
        y_signal[i] = sum_01 + sum_23
    # EVOLVE-BLOCK-END
    return y_signal