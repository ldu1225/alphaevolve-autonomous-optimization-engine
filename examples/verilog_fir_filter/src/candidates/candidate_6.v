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
                reg [15:0] s0, s1, s2, s3, s4, s5, s6, s7;

                // Zero-cost bitwise shifts to represent symmetric tap coefficients (1, 2, 4, 8, 8, 4, 2, 1)
                s0 = x_pipe[0];
                s1 = x_pipe[1] << 1;
                s2 = x_pipe[2] << 2;
                s3 = x_pipe[3] << 3;
                s4 = x_pipe[4] << 3;
                s5 = x_pipe[5] << 2;
                s6 = x_pipe[6] << 1;
                s7 = x_pipe[7];

                // Flat addition of 8 terms enables the synthesis tool to extract a highly optimized
                // Carry-Save Adder (CSA) tree, minimizing critical path propagation delay and gate area.
                y_out <= s0 + s1 + s2 + s3 + s4 + s5 + s6 + s7;
            end
            // EVOLVE-BLOCK-END
        end
    end

endmodule
