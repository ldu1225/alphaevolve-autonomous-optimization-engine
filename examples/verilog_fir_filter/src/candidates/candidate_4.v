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
                // Step 1: Define scaled symmetric terms using intermediate variables for readability
                reg [15:0] x0, x1, x2, x3, x4, x5, x6, x7;
                x0 = x_pipe[0];
                x1 = x_pipe[1] << 1; // Coefficient 2
                x2 = x_pipe[2] << 2; // Coefficient 4
                x3 = x_pipe[3] << 3; // Coefficient 8
                x4 = x_pipe[4] << 3; // Coefficient 8
                x5 = x_pipe[5] << 2; // Coefficient 4
                x6 = x_pipe[6] << 1; // Coefficient 2
                x7 = x_pipe[7];

                // Step 2: Single multi-operand summation to trigger global CSA tree synthesis.
                // This merges all additions into one globally-optimized compressor tree, 
                // leaving only a single final carry-propagation stage, maximizing PPA performance.
                y_out <= x0 + x1 + x2 + x3 + x4 + x5 + x6 + x7;
            end
            // EVOLVE-BLOCK-END
        end
    end

endmodule
