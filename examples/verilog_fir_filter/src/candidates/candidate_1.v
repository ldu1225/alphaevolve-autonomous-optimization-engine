// Enterprise Semiconductor OLED DDI 8-Tap Symmetric FIR Filter Core - Synthesizable Verilog RTL
module oled_ddi_fir_filter (
    input  wire        clk,
    input  wire        rst_n,
    input  wire [15:0] x_in,
    output reg  [15:0] y_out
);
    reg [15:0] x_pipe [0:7];

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            x_pipe[0] <= 16'd0; x_pipe[1] <= 16'd0; x_pipe[2] <= 16'd0; x_pipe[3] <= 16'd0;
            x_pipe[4] <= 16'd0; x_pipe[5] <= 16'd0; x_pipe[6] <= 16'd0; x_pipe[7] <= 16'd0;
            y_out <= 16'd0;
        end else begin
            x_pipe[0] <= x_in;      x_pipe[1] <= x_pipe[0]; x_pipe[2] <= x_pipe[1]; x_pipe[3] <= x_pipe[2];
            x_pipe[4] <= x_pipe[3]; x_pipe[5] <= x_pipe[4]; x_pipe[6] <= x_pipe[5]; x_pipe[7] <= x_pipe[6];

            // EVOLVE-BLOCK-START
            begin : symmetric_fir_filter_core
                // Step 1: Pre-add symmetric inputs to leverage tap symmetry
                reg [15:0] s0, s1, s2, s3;
                // Step 2: Zero-cost bitwise left shifts (replacing multipliers)
                reg [15:0] t1, t2, t3;
                // Step 3: Balanced adder tree intermediate stages
                reg [15:0] stage1_0, stage1_1;

                // Pair inputs via pre-adders (Symmetry: h[0]=h[7], h[1]=h[6], h[2]=h[5], h[3]=h[4])
                s0 = x_pipe[0] + x_pipe[7];
                s1 = x_pipe[1] + x_pipe[6];
                s2 = x_pipe[2] + x_pipe[5];
                s3 = x_pipe[3] + x_pipe[4];

                // Scaling via bitwise left shifts
                t1 = s1 << 1; // Coefficient 2
                t2 = s2 << 2; // Coefficient 4
                t3 = s3 << 3; // Coefficient 8

                // Balanced adder tree execution
                stage1_0 = s0 + t1;
                stage1_1 = t2 + t3;

                // Non-blocking assignment of the final filtered output
                y_out <= stage1_0 + stage1_1;
            end
            // EVOLVE-BLOCK-END
        end
    end

endmodule
