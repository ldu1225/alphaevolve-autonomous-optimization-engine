def compute_fir_response(x_signal):
    n = len(x_signal)
    y_signal = np.zeros(n, dtype=int)
    # EVOLVE-BLOCK-START
    for i in range(7, n):
        # Step 1: Symmetric Folding to exploit filter symmetry (reduces operations by 50%)
        s0 = x_signal[i] + x_signal[i-7]
        s1 = x_signal[i-1] + x_signal[i-6]
        s2 = x_signal[i-2] + x_signal[i-5]
        s3 = x_signal[i-3] + x_signal[i-4]

        # Step 2: Multiplication-free hardware-efficient constant scaling via left-shifts
        t0 = s0
        t1 = s1 << 1
        t2 = s2 << 2
        t3 = s3 << 3

        # Step 3: Balanced binary adder tree to minimize propagation delay / critical path
        sum_stage1_0 = t0 + t1
        sum_stage1_1 = t2 + t3
        
        y_signal[i] = sum_stage1_0 + sum_stage1_1
    # EVOLVE-BLOCK-END
    return y_signal