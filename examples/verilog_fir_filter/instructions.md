# Enterprise OLED DDI 8-Tap Symmetric FIR Filter PPA Optimization

You are a Senior Semiconductor RTL Design Architect. Your task is to optimize the 8-Tap FIR Filter algorithm inside `// EVOLVE-BLOCK-START` and `// EVOLVE-BLOCK-END` for Enterprise OLED Display Driver IC (DDI) pixel noise suppression.

## Technical Goal

Optimize the 8-tap FIR filter `compute_fir_response(x_signal)` to:
- Maximize the target metric `ppa_fitness_score`.
- Preserve pixel noise filtering accuracy (Target MSE error threshold < 0.1).
- Minimize chip power consumption, gate area, and signal propagation delay.

## Function Signature

```python
def compute_fir_response(x_signal: np.ndarray) -> np.ndarray:
    """
    Args:
        x_signal: np.ndarray of shape (N,) — 16-bit Fixed Point Integer Input Pixel Array

    Returns:
        y_signal: np.ndarray of shape (N,) — Filtered Output Pixel Array
    """
```

## Constraints

- Output array size must match input array size `N`.
- Pixel accuracy must satisfy the high-frequency OLED noise removal specification.
- All operations must be valid synthesizable fixed-point operations.

## Available Libraries

- `numpy` (imported as `np`)
- Standard Python math & bitwise operators

## Code Formatting & Readability Guidelines

- Avoid single-line long expressions with heavily nested parentheses `((a + b) + ((c + d) << 1))`.
- Use clear intermediate temporary variables (e.g. `s0 = ...`, `s1 = ...`, `stage1_a = ...`) to maintain hardware RTL pipeline readability and balance signal arrival times.

## Baselines

- The seed program uses 8 hand-crafted 16-bit hardware multipliers.
- It achieves a baseline PPA fitness score around 0.5200.
- An optimal evolved program should achieve a significantly higher `ppa_fitness_score`.

