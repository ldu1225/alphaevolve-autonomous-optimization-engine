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
            begin : filter_opt
                reg [15:0] sum0, sum1, sum2, sum3;
                reg [14:0] stage1_0_upper;
                reg [12:0] stage1_1_upper;
                reg [13:0] y_out_upper;

                // Step 1: Pre-add symmetric taps (16-bit)
                sum0 = x_pipe[0] + x_pipe[7];
                sum1 = x_pipe[1] + x_pipe[6];
                sum2 = x_pipe[2] + x_pipe[5];
                sum3 = x_pipe[3] + x_pipe[4];

                // Step 2: Balanced adder tree with optimized reduced bit-widths
                stage1_0_upper = sum0[15:1] + sum1[14:0];
                stage1_1_upper = sum2[13:1] + sum3[12:0];

                // Step 3: Final accumulation with optimized 14-bit addition
                y_out_upper = stage1_0_upper[14:1] + {stage1_1_upper[12:0], sum2[0]};

                // Step 4: Output assignment
                y_out <= {y_out_upper, stage1_0_upper[0], sum0[0]};
            end
            // EVOLVE-BLOCK-END
        end
    end

endmodule
