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
                reg [15:0] p0, p1, p2, p3;
                reg [15:0] s0, s1, s2, s3;
                reg [15:0] stage1_0, stage1_1;

                // 1. Pre-adders: Leverage tap coefficient symmetry to pair inputs first.
                // This significantly reduces the gate count and simplifies subsequent adder tree logic.
                p0 = x_pipe[0] + x_pipe[7];
                p1 = x_pipe[1] + x_pipe[6];
                p2 = x_pipe[2] + x_pipe[5];
                p3 = x_pipe[3] + x_pipe[4];

                // 2. Zero-cost bitwise shifts representing symmetric tap coefficients (1, 2, 4, 8)
                s0 = p0;
                s1 = p1 << 1;
                s2 = p2 << 2;
                s3 = p3 << 3;

                // 3. Balanced Adder Tree: Minimizes critical path propagation delay and gate area.
                stage1_0 = s0 + s1;
                stage1_1 = s2 + s3;

                y_out <= stage1_0 + stage1_1;
            end
            // EVOLVE-BLOCK-END
        end
    end

endmodule
