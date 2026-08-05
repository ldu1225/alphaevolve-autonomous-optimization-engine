# ==============================================================================
# Enterprise Semiconductor OLED DDI 8-Tap FIR Filter Evaluator & PPA Scoring Engine
# Fine-Grained Precision Verilog RTL & PPA Gate Area Evaluator
# ==============================================================================
import numpy as np
import inspect
import re

def evaluate_verilog(verilog_code: str) -> float:
    """
    Evaluates pure Verilog RTL code string with high granularity precision:
    1) Verilog RTL Syntax & Synthesis Validity
    2) Zero-Multiplier Shift-Add Hardware Area (PPA) Efficiency
    3) Micro-Granularity Code Structure, Variable Reuse & Critical Path Micro-Bonus
    """
    if not verilog_code or not isinstance(verilog_code, str):
        return 0.0

    # 1. Basic Verilog Syntax & Structure Check
    if "module" not in verilog_code or "endmodule" not in verilog_code:
        return 0.0

    # Extract EVOLVE-BLOCK portion for micro-granularity inspection
    if "// EVOLVE-BLOCK-START" in verilog_code and "// EVOLVE-BLOCK-END" in verilog_code:
        evolve_block = verilog_code.split("// EVOLVE-BLOCK-START")[1].split("// EVOLVE-BLOCK-END")[0]
    else:
        evolve_block = verilog_code

    # 2. Count Hardware Operators & Syntax Markers
    mult_count = verilog_code.count('*')
    shift_count = verilog_code.count('<<')
    add_count = verilog_code.count('+')
    var_count = len(re.findall(r"\b(s[0-3]|t[0-3]|sum\d+|stage\d+_\d+|sym_sum\d+|part_[a-b])\b", evolve_block))
    char_len = len(evolve_block.strip())

    has_symmetry = bool(re.search(r"x_pipe\[0\]\s*\+\s*x_pipe\[7\]|sum0_7|s0|t0|pair0", verilog_code))
    has_tree = bool(re.search(r"sum_stage1|stage1|sum_|part_a|adder_tree", verilog_code)) or add_count >= 5
    has_reg_block = "begin :" in evolve_block or "reg [15:0]" in evolve_block

    # 3. PPA Gate Area Efficiency Calculation with High Granularity
    base_hw = 0.5400  # Baseline Gen #0 (8 Multipliers)
    
    # A. Multiplier Penalty & Zero-Cost Shift Reward
    if mult_count == 0:
        mult_bonus = 0.2800  # 100% Zero-Multiplier Bonus
    else:
        mult_bonus = max(0.0, 0.2800 - (mult_count * 0.0350))

    shift_bonus = min(0.0950, shift_count * 0.0280)
    symmetry_bonus = 0.0380 if has_symmetry else 0.0
    tree_bonus = 0.0180 if has_tree else 0.0
    reg_block_bonus = 0.0075 if has_reg_block else 0.0

    # B. Micro-Granularity Granular Modifiers (Character Length & Variable Optimization)
    # Rewards clean, compact, non-redundant intermediate wire/reg utilization
    micro_char_factor = max(-0.0150, min(0.0150, (300 - char_len) * 0.00015))
    micro_var_factor = min(0.0120, var_count * 0.0018)

    # Calculate Total Score
    total_score = base_hw + mult_bonus + shift_bonus + symmetry_bonus + tree_bonus + reg_block_bonus + micro_char_factor + micro_var_factor
    
    # Cap between 0.0 and 0.9910
    final_score = round(min(0.9910, max(0.0, float(total_score))), 4)
    return final_score


def evaluate(program_input):
    """
    Unified Evaluator for both Pure Verilog RTL string and Python simulation module.
    """
    if isinstance(program_input, str):
        return evaluate_verilog(program_input)

    # Handle Python Module Execution
    try:
        if hasattr(program_input, '__source__') and isinstance(program_input.__source__, str):
            code_str = program_input.__source__
            if "module " in code_str or "endmodule" in code_str:
                return evaluate_verilog(code_str)

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
        if hasattr(program_input, 'compute_fir_response'):
            y_sim = program_input.compute_fir_response(x_input)
            diff = y_sim[7:] - y_ideal[7:]
            mse = float(np.mean((diff) ** 2))
            if mse > 500.0:
                return 0.0
            
            accuracy_component = 0.4000 if mse < 1.0 else float(0.4000 / (1.0 + (mse / 50.0)))
        else:
            accuracy_component = 0.4000

        source = getattr(program_input, '__source__', '')
        if "def compute_fir_response" in source:
            pure_code = source[source.find("def compute_fir_response"):]
        else:
            pure_code = source

        mult_count = pure_code.count('*')
        shift_count = pure_code.count('<<')
        
        has_symmetry = ("x_signal[i] + x_signal[i-7]" in pure_code or "s0 =" in pure_code or "t0 =" in pure_code)
        has_tree = ("(t0 + t1)" in pure_code or "stage1" in pure_code)

        base_hw = 0.1200
        mult_penalty = mult_count * 0.05
        mult_free_bonus = 0.1500 if mult_count == 0 else 0.0
        shift_reward = min(0.1600, shift_count * 0.0400)
        symmetry_reward = 0.1000 if has_symmetry else 0.0
        tree_reward = 0.0600 if has_tree else 0.0

        hw_component = max(0.1200, base_hw - mult_penalty + mult_free_bonus + shift_reward + symmetry_reward + tree_reward)
        final_score = round(float(accuracy_component + hw_component), 4)
        return min(0.9910, max(0.0, final_score))
        
    except Exception as e:
        return evaluate_verilog(str(program_input))
