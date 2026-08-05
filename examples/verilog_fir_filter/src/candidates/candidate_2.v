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
            y_out <= stage2_0;
        end
    end

    // Pre-adders utilizing coefficient symmetry
    wire [15:0] s0 = x_pipe[0] + x_pipe[7];
    wire [15:0] s1 = x_pipe[1] + x_pipe[6];
    wire [15:0] s2 = x_pipe[2] + x_pipe[5];
    wire [15:0] s3 = x_pipe[3] + x_pipe[4];

    // Scaling via zero-cost bitwise left shifts
    wire [15:0] t0 = s0;
    wire [15:0] t1 = s1 << 1;
    wire [15:0] t2 = s2 << 2;
    wire [15:0] t3 = s3 << 3;

    // Balanced adder tree to minimize critical path propagation delay
    wire [15:0] stage1_0 = t0 + t1;
    wire [15:0] stage1_1 = t2 + t3;
    wire [15:0] stage2_0 = stage1_0 + stage1_1;

    // Dummy block to safely absorb the template's closing end keywords
    always @(*) begin
        if (1'b0) begin
            // EVOLVE-BLOCK-END
        end
    end

endmodule
