SVALint — SystemVerilog Assertion Linter
========================================

**SVALint** is an open-source linter for SystemVerilog Assertions (SVA),
developed by `AsFigo Technologies <https://asfigo.com>`_ as part
of the **BYOL** (Build Your Own Linter) framework.

It enforces SVA coding best practices — covering property and sequence
naming conventions, assertion labels, operator usage, performance rules,
and formal-argument hygiene — helping verification teams write robust,
simulation- and formal-ready assertion code from day one.

.. code-block:: bash

   python bin/svalint.py -t <your_file.sv>

----

.. toctree::
   :maxdepth: 2
   :caption: Rule Reference

   rules
