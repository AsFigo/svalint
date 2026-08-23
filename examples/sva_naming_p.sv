// ----------------------------------------------------
// SPDX-FileCopyrightText: AsFigo Technologies, UK
// SPDX-FileCopyrightText: VerifWorks, India
// SPDX-License-Identifier: MIT
// ----------------------------------------------------

// Correct: property prefixed with p_, assert has label and fail action block
module sva_naming_good;

  bit clk;
  bit req, gnt;

  property p_req_gnt;
    @(posedge clk) req |-> ##1 gnt;
  endproperty : p_req_gnt

  a_req_gnt: assert property (p_req_gnt)
    else $error("req=%0b gnt=%0b", req, gnt);

endmodule
