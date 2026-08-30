module tb_toggle_module;

  logic clk = 0;
  logic rst_n = 0;
  logic toggle = 0;
  logic out;

  
  toggle_module dut (
    .clk(clk),
    .rst_n(rst_n),
    .toggle(toggle),
    .out(out)
  );

  
  always #5 clk = ~clk;

  
  property p_toggle_behavior;
    @(posedge clk) disable iff (!rst_n)
      $stable(out) or toggle;
  endproperty

  a1 : assert property (p_toggle_behavior)
       else begin
         $error("Assertion FAILED: 'out' changed without 'toggle' being high.");
       end

  // Stimulus
  initial begin
    $display("Starting toggle_module test");

    rst_n = 0; toggle = 0; #12;
    rst_n = 1;             #10;

    toggle = 0;            #10;  // No toggle, output should remain stable
    toggle = 1;            #10;  // Toggle = 1, output should flip
    toggle = 0;            #10;  // No toggle, output should remain stable

    // Illegal condition: manually flip output to simulate assertion failure
    force out = ~out;      #10;  // out changes without toggle = 1 → triggers assertion
    release out;

    #20;
    $display("Test completed");
    $finish;
  end

endmodule
