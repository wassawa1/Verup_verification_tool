
module top (
    input clk,
    input rst_n,
    input [7:0] data_in,
    output [7:0] data_out
);

    reg [7:0] data_reg;
    
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n)
            data_reg <= 8'h00;
        else
            data_reg <= data_in;
    end
    
    assign data_out = data_reg;

endmodule
