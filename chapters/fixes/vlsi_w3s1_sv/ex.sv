module xor_assign (input logic a, b, output logic y);
    assign y = a ^ b;
endmodule

module xor_comb (input logic a, b, output logic y);
    always_comb begin
        if (a == b)
            y = 1'b0;
        else
            y = 1'b1;
    end
endmodule

module tb_xor;
    logic a, b, y1, y2;
    int errors = 0;
    xor_assign u1 (.a(a), .b(b), .y(y1));
    xor_comb   u2 (.a(a), .b(b), .y(y2));
    initial begin
        for (int i = 0; i < 4; i++) begin
            {a, b} = i;
            #10;
            $display("a=%b b=%b -> %b %b", a, b, y1, y2);
            if (y1 !== y2) errors++;
        end
        if (errors == 0) $display("OK: same truth table");
        else             $display("ERROR: %0d differences", errors);
        $finish;
    end
endmodule

module hex7seg_en (
    input  logic [3:0] x,
    input  logic       en,
    output logic [6:0] seg
);
    logic [6:0] pat;
    hex7seg u (.x(x), .seg(pat));
    assign seg = en ? pat : 7'b0000000;   // en = 0 -> display dark
endmodule

module tb_en;
    logic [3:0] x; logic en; logic [6:0] seg;
    hex7seg_en d (.x(x), .en(en), .seg(seg));
    initial begin
        x = 4'h3; en = 1; #10; $display("en=1 x=3 seg=%b", seg);
        en = 0; #10; $display("en=0 x=3 seg=%b", seg);
        $finish;
    end
endmodule
