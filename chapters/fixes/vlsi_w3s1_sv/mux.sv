module mux2_assign (
    input  logic a, b, s,
    output logic y
);
    assign y = s ? b : a;          // one line: a wire that is always connected
endmodule

module mux2_comb (
    input  logic a, b, s,
    output logic y
);
    always_comb begin              // a block of steps, re-run whenever a, b or s change
        if (s)
            y = b;
        else
            y = a;
    end
endmodule
