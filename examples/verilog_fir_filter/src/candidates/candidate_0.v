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
            // AS-IS Baseline: 8 Expensive Hardware Multipliers (Coefficients: 1, 2, 4, 8, 8, 4, 2, 1)
            y_out <= (x_pipe[0] * 16'd1) + (x_pipe[1] * 16'd2) + (x_pipe[2] * 16'd4) + (x_pipe[3] * 16'd8) +
                     (x_pipe[4] * 16'd8) + (x_pipe[5] * 16'd4) + (x_pipe[6] * 16'd2) + (x_pipe[7] * 16'd1);
            // EVOLVE-BLOCK-END
        end
    end

endmodule
