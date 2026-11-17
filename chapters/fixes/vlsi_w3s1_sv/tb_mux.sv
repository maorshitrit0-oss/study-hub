module tb_mux;
    logic a, b, s;
    logic y1, y2;
    int   errors = 0;

    mux2_assign u1 (.a(a), .b(b), .s(s), .y(y1));
    mux2_comb   u2 (.a(a), .b(b), .s(s), .y(y2));

    initial begin
        for (int i = 0; i < 8; i++) begin
            {s, a, b} = i;                 // all 8 combinations of the 3 inputs
            #10;
            $display("s=%b a=%b b=%b -> assign:%b always_comb:%b", s, a, b, y1, y2);
            if (y1 !== y2) errors++;
        end
        if (errors == 0) $display("OK: both muxes agree on all 8 inputs");
        else             $display("ERROR: %0d differences", errors);
        $finish;
    end
endmodule
