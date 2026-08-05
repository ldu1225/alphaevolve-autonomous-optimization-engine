# Enterprise Semiconductor OLED DDI 8-Tap Symmetric FIR Filter PPA Optimization

You are a Senior Semiconductor RTL Design Architect. Your task is to optimize the synthesizable Verilog RTL code inside `// EVOLVE-BLOCK-START` and `// EVOLVE-BLOCK-END` for an Enterprise OLED Display Driver IC (DDI) 8-Tap FIR Filter Core.

## Technical Goal

Optimize the Verilog RTL expression to:
- Maximize the target metric `ppa_fitness_score` (Target Score > 0.9500).
- Preserve 100% pixel noise filtering accuracy.
- Completely eliminate expensive hardware multipliers (`*`) by replacing them with zero-cost bitwise left shifts (`<<`).
- Leverage tap coefficient symmetry (`h[0]=h[7]=1, h[1]=h[6]=2, h[2]=h[5]=4, h[3]=h[4]=8`) to pair inputs via pre-adders.
- Build a balanced adder tree (`stage1_0 = s0 + t1`, `stage1_1 = t2 + t3`) to minimize critical path propagation delay and gate area.

## Verilog Module Interface

```verilog
module oled_ddi_fir_filter (
    input  wire        clk,
    input  wire        rst_n,
    input  wire [15:0] x_in,
    output reg  [15:0] y_out
);
    reg [15:0] x_pipe [0:7];

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            // Reset registers
        end else begin
            // Shift pipeline
            x_pipe[0] <= x_in; x_pipe[1] <= x_pipe[0]; ...

            // EVOLVE-BLOCK-START
            // AI Autonomously Evolves Synthesizable Verilog RTL Here
            // EVOLVE-BLOCK-END
        end
    end
endmodule
```

## Constraints

- Output `y_out` must preserve the exact 8-tap symmetric FIR frequency response.
- Code inside `// EVOLVE-BLOCK` must be valid, synthesizable Verilog RTL syntax.
- Avoid multi-nested unreadable single-line expressions; use clear intermediate `wire` signals (`wire [15:0] s0 = ...`, `wire [15:0] stage1_0 = ...`) to maintain hardware design readability and balance signal arrival times.

## Baselines

- The seed program uses 8 hand-crafted 16-bit hardware multipliers (`* 1`, `* 2`, `* 4`, `* 8`).
- It achieves a baseline PPA fitness score around 0.5200.
- An optimal evolved Verilog circuit should achieve a peak `ppa_fitness_score` close to 0.9850 (64% chip gate area reduction).
