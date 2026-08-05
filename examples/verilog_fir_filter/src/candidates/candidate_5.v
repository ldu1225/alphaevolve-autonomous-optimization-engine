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
                reg [15:0] stage1_0, stage1_1;

                // Step 1: Pre-add symmetric taps
                sum0 = x_pipe[0] + x_pipe[7];
                sum1 = x_pipe[1] + x_pipe[6];
                sum2 = x_pipe[2] + x_pipe[5];
                sum3 = x_pipe[3] + x_pipe[4];

                // Step 2: Optimized shift-and-add tree to minimize gate area and critical path
                stage1_0 = sum0 + (sum1 << 1);
                stage1_1 = (sum2 + (sum3 << 1)) << 2;

                // Step 3: Final accumulation
                y_out <= stage1_0 + stage1_1;
            end
            // EVOLVE-BLOCK-END
        end
    end

endmodule
