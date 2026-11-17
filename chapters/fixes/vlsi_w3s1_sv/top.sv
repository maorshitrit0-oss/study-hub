module top (
    input  logic [7:0] sw,      // SW1..SW4 = the digit, SW7 and SW8 = polarity tests
    output logic [7:0] seg1,    // display 1: segments a..g and the dot
    output logic [3:0] dig1     // display 1: which of the 4 digits is on
);
    logic [6:0] pat;            // the pattern with 1 = segment on

    hex7seg u_dec (.x(sw[3:0]), .seg(pat));

    assign seg1 = sw[7] ? ~{1'b0, pat} : {1'b0, pat};   // SW8 flips the segment polarity (dot stays off)
    assign dig1 = sw[6] ? 4'b0000 : 4'b1111;           // SW7 flips the digit-select polarity
endmodule
