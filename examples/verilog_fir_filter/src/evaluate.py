# ==============================================================================
# Enterprise Semiconductor OLED DDI 8-Tap FIR Filter Evaluator & PPA Scoring Engine
# ==============================================================================
import numpy as np
import inspect

def evaluate(program_module):
    """
    Evaluates 8-Tap OLED DDI FIR Filter candidate code on:
    1) Pixel Filtering Accuracy (MSE Error vs Ideal Response)
    2) Chip PPA (Power, Performance, Area) Gate Area Efficiency
    """
    try:
        # Generate Test Pixel Signal (16-bit Fixed Point Integer Input Stream)
        t = np.linspace(0, 1, 120)
        low_freq = np.sin(2 * np.pi * 5 * t)
        high_noise = 0.5 * np.sin(2 * np.pi * 50 * t)
        x_input = ((low_freq + high_noise) * 100).astype(int)
        
        # 8-Tap Ideal Response (Coefficients: 1, 2, 4, 8, 8, 4, 2, 1)
        y_ideal = np.zeros(120, dtype=int)
        for i in range(7, 120):
            y_ideal[i] = (x_input[i] * 1) + (x_input[i-1] * 2) + (x_input[i-2] * 4) + (x_input[i-3] * 8) + (x_input[i-4] * 8) + (x_input[i-5] * 4) + (x_input[i-6] * 2) + (x_input[i-7] * 1)
        
        # Execute Candidate Filter Simulation
        y_sim = program_module.compute_fir_response(x_input)
        
        # 1) Pixel Filtering Accuracy (MSE Error) - Max 0.4000
        diff = y_sim[7:] - y_ideal[7:]
        mse = float(np.mean((diff) ** 2))
        if mse > 500.0:
            return 0.0
        
        if mse < 1.0:
            accuracy_component = 0.4000
        else:
            accuracy_component = float(0.4000 / (1.0 + (mse / 50.0)))
        
        # 2) PPA Hardware Gate Area & Operation Inspection - Max 0.5800
        source = ""
        try:
            if hasattr(program_module, '__source__') and program_module.__source__:
                source = program_module.__source__
            elif hasattr(program_module, '__code_str__') and program_module.__code_str__:
                source = program_module.__code_str__
            elif hasattr(program_module, 'compute_fir_response') and hasattr(program_module.compute_fir_response, '__source__'):
                source = program_module.compute_fir_response.__source__
            else:
                source = inspect.getsource(program_module.compute_fir_response)
        except Exception:
            source = getattr(program_module, '__source__', getattr(program_module, '__code_str__', ''))

        # Extract pure function code
        if "def compute_fir_response" in source:
            pure_code = source[source.find("def compute_fir_response"):]
        else:
            pure_code = source

        mult_count = pure_code.count('*')
        shift_count = pure_code.count('<<')
        
        has_symmetry = ("x_signal[i] + x_signal[i-7]" in pure_code or "x[i] + x[i-7]" in pure_code or
                        "s0 =" in pure_code or "s1 =" in pure_code or "t0 =" in pure_code)
        
        has_tree = ("(t0 + t1)" in pure_code or "(s0 + s1)" in pure_code or 
                    "stage1" in pure_code or "part_a" in pure_code)

        # Code Readability Inspection
        is_ugly_nested = pure_code.count("((") >= 3 and "\n        s0 =" not in pure_code and "\n        t0 =" not in pure_code
        readability_bonus = 0.0500 if (has_symmetry and not is_ugly_nested) else 0.0
        readability_penalty = -0.0500 if is_ugly_nested else 0.0

        base_hw = 0.1200
        mult_penalty = mult_count * 0.05
        mult_free_bonus = 0.1500 if mult_count == 0 else 0.0
        shift_reward = min(0.1600, shift_count * 0.0400)
        symmetry_reward = 0.1000 if has_symmetry else 0.0
        tree_reward = 0.0600 if has_tree else 0.0

        hw_component = max(0.1200, base_hw - mult_penalty + mult_free_bonus + shift_reward + symmetry_reward + tree_reward + readability_bonus + readability_penalty)
        
        final_score = round(float(accuracy_component + hw_component), 4)
        return min(0.9850, max(0.0, final_score))
        
    except Exception as e:
        print("Evaluation Exception:", e)
        return 0.0
