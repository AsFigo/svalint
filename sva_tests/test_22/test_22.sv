module toggle_module (
  input  logic clk,
  input  logic rst_n,
  input  logic toggle,
  output logic out
);

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n)
      out <= 0;
    else if (toggle)
      out <= ~out;
  end

endmodule
