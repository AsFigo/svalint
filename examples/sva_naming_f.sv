// ----------------------------------------------------
// SPDX-FileCopyrightText: AsFigo Technologies, UK
// SPDX-FileCopyrightText: VerifWorks, India
// SPDX-License-Identifier: MIT
// ----------------------------------------------------

// Violation: property name does not start with p_ (PROP_NAMING)
// Violation: assert statement missing a label (ASSERT_MISSING_LABEL)
module sva_naming_bad;

  bit clk;
  bit req, gnt;

  property chk_req_gnt;
    @(posedge clk) req |-> ##1 gnt;
  endproperty : chk_req_gnt

  assert property (chk_req_gnt)
    else $error("req=%0b gnt=%0b", req, gnt);

endmodule
