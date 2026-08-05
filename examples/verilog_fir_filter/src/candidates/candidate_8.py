def compute_fir_response(x_signal):
    n = len(x_signal)
    y_signal = np.zeros(n, dtype=int)
    # EVOLVE-BLOCK-START
    for i in range(7, n):
        # Stage 1: Symmetric pre-additions to reduce gate area and power
        sum_0_7 = x_signal[i] + x_signal[i-7]
        sum_1_6 = x_signal[i-1] + x_signal[i-6]
        sum_2_5 = x_signal[i-2] + x_signal[i-5]
        sum_3_4 = x_signal[i-3] + x_signal[i-4]

        # Stage 2: Scaling via bit-shifts (eliminates costly hardware multipliers)
        term_0 = sum_0_7
        term_1 = sum_1_6 << 1
        term_2 = sum_2_5 << 2
        term_3 = sum_3_4 << 3

        # Stage 3: Balanced adder tree to minimize propagation delay (critical path)
        stage1_a = term_0 + term_1
        stage1_b = term_2 + term_3
        
        y_signal[i] = stage1_a + stage1_b
    # EVOLVE-BLOCK-END
    return y_signal