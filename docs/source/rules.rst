Lint Rules
==========

.. _ASSERT_NAMING:

ASSERT_NAMING
-------------

Assert label must start with ``a_``.

**Rationale**: A consistent ``a_`` prefix on assertion labels allows engineers
to instantly distinguish assertions from assumptions (``m_``) and cover
directives (``c_``) in log files, waveforms, and formal reports without
reading the full directive syntax.

**Violation**::

    req_ack: assert property (@(posedge clk) req |-> ##[1:3] ack);

**Correct usage**::

    a_req_ack: assert property (@(posedge clk) req |-> ##[1:3] ack);

**Severity**: WARNING

----

.. _ASSERT_MISSING_LABEL:

ASSERT_MISSING_LABEL
--------------------

Assert statements must have a label.

**Rationale**: Labels on assertions enable targeted waveform search, log
filtering, and coverage reporting. Without a label, tracing a failing
assertion back to its source in a large design is time-consuming. Most
formal and simulation tools can filter and report assertions by label.

**Violation**::

    assert property (@(posedge clk) req |-> ##[1:3] ack);

**Correct usage**::

    a_req_ack: assert property (@(posedge clk) req |-> ##[1:3] ack);

**Severity**: ERROR

----

.. _ASSUME_NAMING:

ASSUME_NAMING
-------------

Assume label must start with ``m_``.

**Rationale**: The ``m_`` prefix (model/assume) distinguishes constraint
assumptions from assertions (``a_``) and coverage (``c_``) in formal tool
reports and log files, making intent immediately clear during review.

**Violation**::

    req_stable: assume property (@(posedge clk) $stable(req));

**Correct usage**::

    m_req_stable: assume property (@(posedge clk) $stable(req));

**Severity**: WARNING

----

.. _COVER_NAMING:

COVER_NAMING
------------

Cover label must start with ``c_``.

**Rationale**: A consistent ``c_`` prefix on cover directives distinguishes
coverage intent from assertions (``a_``) and assumptions (``m_``) when
reviewing formal reachability reports and simulation coverage logs.

**Violation**::

    req_seen: cover property (@(posedge clk) req);

**Correct usage**::

    c_req_seen: cover property (@(posedge clk) req);

**Severity**: WARNING

----

.. _FUNC_NO_NON_OLAP_COVER:

FUNC_NO_NON_OLAP_COVER
----------------------

Avoid non-overlapping implication (``|=>``) in cover property.

**Rationale**: Using ``|=>`` with a ``cover property`` directive causes coverage
to be reported one cycle after the trigger, collecting vacuous or false-positive
hits. The cover directive should express direct observability; use ``##1``
or restructure the property to avoid ``|=>``.

**Violation**::

    c_req_ack: cover property (@(posedge clk) req |=> ack);

**Correct usage**::

    c_req_ack: cover property (@(posedge clk) req ##1 ack);

**Severity**: ERROR

----

.. _FUNC_NO_OLAP_COVER:

FUNC_NO_OLAP_COVER
------------------

Avoid overlapping implication (``|->``) in cover property.

**Rationale**: Using ``|->`` with a ``cover property`` directive can collect
vacuous coverage when the antecedent does not hold, giving a false sense of
coverage completeness. Use ``##0`` for same-cycle coverage or restructure
without implication.

**Violation**::

    c_req_ack: cover property (@(posedge clk) req |-> ack);

**Correct usage**::

    c_req_ack: cover property (@(posedge clk) req ##0 ack);

**Severity**: ERROR

----

.. _FUNC_MISSING_FAIL_ABLK:

FUNC_MISSING_FAIL_ABLK
----------------------

Assert statement must have a fail action block.

**Rationale**: Without an ``else`` fail action block, a failing assertion
produces only a generic simulator error with no design-context information.
A fail action block with ``$error`` or ``$fatal`` lets you print signal
values, timestamps, and custom messages, drastically reducing debug time.

**Violation**::

    a_req_ack: assert property (@(posedge clk) req |-> ##[1:3] ack);

**Correct usage**::

    a_req_ack: assert property (@(posedge clk) req |-> ##[1:3] ack)
        else $error("req=%0b ack=%0b", req, ack);

**Severity**: ERROR

----

.. _FUNC_AVOID_$_RANGE_IN_CONSEQ_A:

FUNC_AVOID_$_RANGE_IN_CONSEQ_A
------------------------------

Avoid unbounded ``##[0:$]`` range in assertion consequent.

**Rationale**: An assertion with an infinite range (``$``) in its consequent
can never FAIL — it will always find a future cycle where the condition holds,
or wait indefinitely. This makes the assertion useless for verification. Use
a deterministic bounded delay instead.

**Violation**::

    a_ack: assert property (@(posedge clk) $rose(req) |-> ##[0:$] ack);

**Correct usage**::

    a_ack: assert property (@(posedge clk) $rose(req) |-> ##[1:8] ack);

**Severity**: ERROR

**References**: Ben Cohen, *SVA Handbook* https://payhip.com/b/7HvMk

----

.. _DBG_MISS_END_LBL_PROP:

DBG_MISS_END_LBL_PROP
---------------------

Property declaration must have an end-label.

**Rationale**: End-labels (e.g., ``endproperty: p_my_prop``) create a visual
bracket around the property body, making it easier to identify boundaries in
large files and enabling consistent navigation in editors. They are especially
valuable when properties span many lines.

**Violation**::

    property p_req_ack;
        @(posedge clk) req |-> ##[1:3] ack;
    endproperty

**Correct usage**::

    property p_req_ack;
        @(posedge clk) req |-> ##[1:3] ack;
    endproperty: p_req_ack

**Severity**: ERROR

----

.. _DBG_MISS_END_LBL_SEQ:

DBG_MISS_END_LBL_SEQ
--------------------

Sequence declaration must have an end-label.

**Rationale**: End-labels (e.g., ``endsequence: s_my_seq``) visually bracket
the sequence body and improve navigability in large files. They are especially
valuable in deeply nested or multi-line sequence definitions.

**Violation**::

    sequence s_req_rise;
        @(posedge clk) ##1 $rose(req);
    endsequence

**Correct usage**::

    sequence s_req_rise;
        @(posedge clk) ##1 $rose(req);
    endsequence: s_req_rise

**Severity**: ERROR

----

.. _NO_AA_EXISTS_SVA:

NO_AA_EXISTS_SVA
----------------

Avoid associative array ``exists()`` method inside SVA.

**Rationale**: IEEE LRM 1800 §16.6 requires sampled associative array elements
to persist until assertion evaluation completes, but many EDA tools have not
fully adopted this requirement and impose restrictions or prohibit it entirely.
Avoid ``exists()`` inside SVA to maintain broad tool compatibility.

**Violation**::

    a_mem: assert property (@(posedge clk)
        (valid, v=mem.exists(addr)) |-> v);

**Correct usage**: Sample the ``exists()`` result into a logic signal in an
always block and reference that signal in SVA.

**Severity**: ERROR

**References**: IEEE 1800 LRM §16.6. Rule suggested by Ben Cohen.

----

.. _FUNC_AVOID_DOLLAR_TIME:

FUNC_AVOID_DOLLAR_TIME
----------------------

Use ``$realtime`` instead of ``$time`` in SVA.

**Rationale**: ``$time`` returns an integer truncated to simulation time
precision, losing sub-precision timing information. ``$realtime`` returns
a real-valued time that accurately reflects actual simulation time, which
is essential for timing assertions where sub-precision differences matter.

**Violation**::

    a_timeout: assert property (@(posedge clk)
        start |-> ($time - t0 < TIMEOUT));

**Correct usage**::

    a_timeout: assert property (@(posedge clk)
        start |-> ($realtime - t0 < TIMEOUT));

**Severity**: ERROR

----

.. _STYLE_AVOID_FIRST_MATCH_A:

STYLE_AVOID_FIRST_MATCH_A
-------------------------

Avoid ``first_match()`` in SVA for formal verification.

**Rationale**: ``first_match()`` creates multiple concurrent threads that
formal tools must evaluate simultaneously, potentially causing state-space
explosion and degraded performance. It also adds complexity that makes
failures harder to debug. While acceptable in simulation, it is generally
discouraged for formal analysis.

**Violation**::

    a_req: assert property (@(posedge clk)
        first_match(req ##[1:5] ack) |-> done);

**Correct usage**: Restructure using deterministic timing or goto repetition
to eliminate the need for ``first_match``.

**Severity**: ERROR

**References**: Ben Cohen, *SVA Handbook* https://payhip.com/b/7HvMk

----

.. _COMPAT_NO_POP_BACK_SVA:

COMPAT_NO_POP_BACK_SVA
----------------------

Avoid queue method ``pop_back()`` inside SVA.

**Rationale**: IEEE LRM 1800 §16.6 requires sampled queue elements to persist
until assertion evaluation completes, but many EDA tools restrict or prohibit
queue method calls inside SVA expressions for performance reasons. Avoid
``pop_back()`` in SVA to ensure broad simulator and formal tool compatibility.

**Violation**::

    a_data: assert property (@(posedge clk)
        $rose(valid) |-> (q.pop_back() == 8'hA5));

**Correct usage**: Sample the queue element into a logic variable in an
always block and reference that variable in SVA.

**Severity**: ERROR

**References**: IEEE 1800 LRM §16.6. Rule suggested by Ben Cohen.

----

.. _COMPAT_NO_POP_FRONT_SVA:

COMPAT_NO_POP_FRONT_SVA
-----------------------

Avoid queue method ``pop_front()`` inside SVA.

**Rationale**: IEEE LRM 1800 §16.6 requires sampled queue elements to persist
until assertion evaluation completes, but many EDA tools restrict or prohibit
queue method calls inside SVA. Avoid ``pop_front()`` in SVA for broad
simulator and formal tool compatibility.

**Violation**::

    a_data: assert property (@(posedge clk)
        $rose(valid) |-> (q.pop_front() == 8'hA5));

**Correct usage**: Sample the queue element into a logic variable in an
always block and reference that variable in SVA.

**Severity**: ERROR

**References**: IEEE 1800 LRM §16.6. Rule suggested by Ben Cohen.

----

.. _STYLE_AVOID_RANGE_IN_ANT_A:

STYLE_AVOID_RANGE_IN_ANT_A
--------------------------

Avoid cycle ranges in assertion antecedent.

**Rationale**: Range repetition in an antecedent (e.g., ``##[1:10]``) creates
multiple concurrent threads, one per possible delay value. Only one thread
can be non-vacuous while others generate spurious vacuous passes. Use goto
repetition (``[->1]``) to ensure exactly one match thread.

**Violation**::

    a_rdy: assert property (@(posedge clk)
        $rose(req) ##[1:10] rdy |-> ##[1:2] ack);

**Correct usage**::

    a_rdy: assert property (@(posedge clk)
        $rose(req) ##1 rdy[->1] |-> ##[1:2] ack);

**Severity**: ERROR

**References**: Ben Cohen, *SVA Handbook* https://payhip.com/b/7HvMk §2.2.2.2

----

.. _REUSE_NO_TIMELITERAL:

REUSE_NO_TIMELITERAL
--------------------

Avoid explicit time literals in SVA property declarations.

**Rationale**: Hard-coded time values (e.g., ``10ns``, ``100ps``) in SVA make
properties non-reusable across designs with different clock frequencies or
timing budgets. Use parameters or `` `define`` macros so timing can be
adjusted without modifying the assertion source.

**Violation**::

    p_timeout: property (@(posedge clk)
        start |-> done within 100ns);

**Correct usage**::

    parameter TIMEOUT_CYCLES = 20;
    p_timeout: property (@(posedge clk)
        start |-> ##[1:TIMEOUT_CYCLES] done);

**Severity**: ERROR

----

.. _STYLE_AVOID_WITHIN_A:

STYLE_AVOID_WITHIN_A
--------------------

Avoid the ``within`` sequence operator in SVA.

**Rationale**: The ``within`` operator, while part of the LRM, has misleading
semantics that frequently cause incorrect assertion intent. Its interaction
with threading and overlap semantics is non-intuitive, leading to assertions
that appear correct but check something different from what was intended.
Explicit sequence composition using ``##`` and repetition operators is clearer
and more portable.

**Violation**::

    a_ack: assert property (@(posedge clk)
        (req ##1 ack) within (start ##[1:10] stop));

**Correct usage**: Express the temporal relationship explicitly using ``##``
delays and repetition without relying on ``within``.

**Severity**: ERROR

**References**: Ben Cohen, *SVA Handbook* https://payhip.com/b/7HvMk

----

.. _PERF_MISSING_IMPLICATION_OPER:

PERF_MISSING_IMPLICATION_OPER
-----------------------------

SVA property without an implication operator hurts simulation performance.

**Rationale**: A property without ``|->`` or ``|=>`` evaluates its consequent
on every active clock edge, creating a continuous evaluation thread with no
gating condition. This significantly degrades simulation performance on large
designs. Add an antecedent with an implication operator to gate evaluation
on meaningful trigger conditions. Exception: the ``forbid`` property style.

**Violation**::

    p_no_x: property (@(posedge clk) !$isunknown(data));

**Correct usage**::

    p_no_x: property (@(posedge clk) valid |-> !$isunknown(data));

**Severity**: ERROR

----

.. _PERF_NO_LARGE_DELAY:

PERF_NO_LARGE_DELAY
-------------------

Avoid large cycle delays (> 100 by default) in SVA properties.

**Rationale**: Large delay values (e.g., ``##500``) force the simulator to
maintain evaluation threads for hundreds of cycles, significantly increasing
memory and runtime overhead. If a large delay is genuinely required, use a
parameterized constant and document the justification. The threshold is
configurable via ``cfgMaxDelay`` (default: 100).

**Violation**::

    p_resp: property (@(posedge clk) req |-> ##500 ack);

**Correct usage**::

    parameter MAX_RESP = 20;
    p_resp: property (@(posedge clk) req |-> ##[1:MAX_RESP] ack);

**Severity**: ERROR

----

.. _PERF_PASS_ACT_BLK:

PERF_PASS_ACT_BLK
-----------------

Assert statement must not have a pass action block.

**Rationale**: A pass action block executes on every successful assertion
evaluation, which can occur millions of times per simulation run. This
severely degrades simulation performance. Pass action blocks are almost
never needed; remove them or use coverage-based approaches instead.

**Violation**::

    a_req_ack: assert property (@(posedge clk) req |-> ack)
        $info("pass");

**Correct usage**::

    a_req_ack: assert property (@(posedge clk) req |-> ack)
        else $error("FAIL: req=%0b ack=%0b", req, ack);

**Severity**: ERROR

----

.. _PERF_AVOID_$_RANGE_IN_ANT_A:

PERF_AVOID_$_RANGE_IN_ANT_A
---------------------------

Avoid unbounded ``##[1:$]`` range in assertion antecedent.

**Rationale**: An unbounded range in the antecedent forces the tool to spawn
and maintain an unbounded number of concurrent threads, one per possible cycle
count. This causes state-space explosion in formal tools and significant
slowdown in simulation. Use a finite bound based on expected design behavior.

**Violation**::

    a_ack: assert property (@(posedge clk)
        req ##[1:$] rdy |-> ack);

**Correct usage**::

    a_ack: assert property (@(posedge clk)
        req ##[1:10] rdy |-> ack);

**Severity**: ERROR

**References**: Ben Cohen, *SVA Handbook* https://payhip.com/b/7HvMk

----

.. _PROP_NAMING:

PROP_NAMING
-----------

Property declaration must start with ``p_``.

**Rationale**: A consistent ``p_`` prefix on property names allows engineers
to instantly identify and filter property declarations in log files, waveforms,
and code search. It also visually separates properties from sequences
(typically ``s_`` prefixed) and module-level signals.

**Violation**::

    property req_ack;
        @(posedge clk) req |-> ##[1:3] ack;
    endproperty: req_ack

**Correct usage**::

    property p_req_ack;
        @(posedge clk) req |-> ##[1:3] ack;
    endproperty: p_req_ack

**Severity**: WARNING

----

.. _REUSE_NO_ONE_LINER_FAIL_ABLK:

REUSE_NO_ONE_LINER_FAIL_ABLK
----------------------------

Fail action block must use ``begin/end``, not a one-liner.

**Rationale**: A one-liner fail action block cannot be extended without
structural refactoring. Using ``begin/end`` from the start allows additional
debug statements, coverage increments, or task calls to be added later
without changing the block structure, improving long-term reusability.

**Violation**::

    a_req_ack: assert property (@(posedge clk) req |-> ack)
        else $error("FAIL");

**Correct usage**::

    a_req_ack: assert property (@(posedge clk) req |-> ack)
        else begin
            $error("FAIL: req=%0b ack=%0b", req, ack);
        end

**Severity**: ERROR

----

.. _DBG_USE_SIMPLE_EXPR_IN_CONSEQ:

DBG_USE_SIMPLE_EXPR_IN_CONSEQ
-----------------------------

Avoid complex consequent expressions; prefer multiple simple properties.

**Rationale**: A property with multiple implication operators or a consequent
containing more than two ``&&`` expressions is difficult to debug when it
fails — the failing sub-expression is not immediately obvious from the error
report. Splitting into smaller properties lets the tool pinpoint exactly which
condition failed.

**Violation**::

    p_complex: property (@(posedge clk)
        req |-> ack && data_valid && !err && count > 0);

**Correct usage**::

    p_ack:   assert property (@(posedge clk) req |-> ack);
    p_valid: assert property (@(posedge clk) req |-> data_valid);
    p_noerr: assert property (@(posedge clk) req |-> !err);

**Severity**: ERROR

----

.. _DELAY_BEFORE_ROSE:

DELAY_BEFORE_ROSE
-----------------

A ``##1`` delay is required immediately before ``$rose``.

**Rationale**: ``$rose(sig)`` samples the signal on two consecutive clocks.
Without a preceding ``##1``, the assertion may fire on the very first active
clock before ``sig`` has a defined previous value, causing spurious failures
at time zero or after resets when signal history is undefined.

**Violation**::

    p_rose_bad: property (@(posedge clk) $rose(req) |-> ack);

**Correct usage**::

    p_rose_ok: property (@(posedge clk) ##1 $rose(req) |-> ack);

**Severity**: ERROR

----

.. _FUNC_AVOID_EV_ALW:

FUNC_AVOID_EV_ALW
-----------------

Avoid ``eventually always`` (Unbounded Weak-Weak).

**Rationale**: Weak ``eventually`` allows the assertion to pass vacuously if
the simulation ends before stabilization is observed. Additionally, expecting
permanent stability in dynamic simulation leads to false failures when system
state is later disturbed by resets or power sequences.

**Violation**::

    a_stab: assert property (@(posedge clk) eventually always stable(data));

**Correct usage**::

    a_stab: assert property (@(posedge clk) s_eventually [1:100] stable(data));

**Severity**: ERROR

----

.. _FUNC_AVOID_EV_S_ALW:

FUNC_AVOID_EV_S_ALW
-------------------

Avoid ``eventually s_always`` (Unbounded Weak-Strong).

**Rationale**: This pattern asserts that a condition will eventually lock into
a permanent strong state. In directed or constrained-random testbenches, this
is highly susceptible to failures when test phases shift (e.g., low-power
entry/exit). Add explicit disable conditions or bound the stability window.

**Violation**::

    a_lock: assert property (@(posedge clk) eventually s_always locked);

**Correct usage**::

    a_lock: assert property (@(posedge clk)
        s_eventually [1:50] locked disable iff (reset));

**Severity**: ERROR

----

.. _FUNC_AVOID_S_EV_ALW:

FUNC_AVOID_S_EV_ALW
-------------------

Avoid ``s_eventually always`` (Unbounded Strong-Weak).

**Rationale**: Asserting that a signal eventually becomes permanently true is
fragile in dynamic simulation. Any subsequent reset, power-gating sequence,
or testbench re-initialization will disturb the signal, producing persistent
false assertion failures.

**Violation**::

    a_stab: assert property (@(posedge clk) s_eventually always stable(data));

**Correct usage**::

    a_stab: assert property (@(posedge clk) s_eventually [1:100] stable(data));

**Severity**: ERROR

----

.. _FUNC_AVOID_S_EV_S_ALW:

FUNC_AVOID_S_EV_S_ALW
---------------------

Avoid ``s_eventually s_always`` (Unbounded Strong-Strong).

**Rationale**: Demanding that a signal stabilizes and holds permanently
is unrealistic in simulation. Any subsequent reset or mode change will
violate this expectation, causing persistent false failures.

**Violation**::

    a_lock: assert property (@(posedge clk) s_eventually s_always locked);

**Correct usage**::

    a_lock: assert property (@(posedge clk)
        s_eventually [1:50] s_always [0:10] locked);

**Severity**: ERROR

----

.. _FUNC_AVOID_WEAK_EVENTUALLY:

FUNC_AVOID_WEAK_EVENTUALLY
--------------------------

Avoid weak ``eventually``; use ``s_eventually``.

**Rationale**: The weak ``eventually`` operator passes vacuously if the
simulation ends before the condition becomes true, making liveness assertions
meaningless — they can never fail. Use ``s_eventually`` (strong eventually)
to enforce that the condition must be observed within the simulation run.

**Violation**::

    a_done: assert property (@(posedge clk) start |-> eventually done);

**Correct usage**::

    a_done: assert property (@(posedge clk) start |-> s_eventually done);

**Severity**: ERROR

----

.. _FUNC_AVOID_BOUNDED_NEXTTIME:

FUNC_AVOID_BOUNDED_NEXTTIME
---------------------------

Avoid bounded weak ``nexttime [k]``; use ``s_nexttime [k]``.

**Rationale**: Bounded weak ``nexttime [k]`` allows vacuously true passes at
simulation limits when insufficient clock cycles remain, potentially masking
functional verification blind spots. Use ``s_nexttime [k]`` to prevent such
vacuous passes.

**Violation**::

    a_nxt: assert property (@(posedge clk) req |-> nexttime [2] ack);

**Correct usage**::

    a_nxt: assert property (@(posedge clk) req |-> s_nexttime [2] ack);

**Severity**: ERROR

----

.. _FUNC_AVOID_NEXTTIME:

FUNC_AVOID_NEXTTIME
-------------------

Avoid unbounded weak ``nexttime``; use ``s_nexttime``.

**Rationale**: Weak ``nexttime`` evaluates to true vacuously if the simulation
ends or clock ticks terminate before the next cycle is observed, making the
assertion ineffective. Use ``s_nexttime`` (strong nexttime) to enforce that
the next-cycle condition is strictly observed.

**Violation**::

    a_nxt: assert property (@(posedge clk) req |-> nexttime ack);

**Correct usage**::

    a_nxt: assert property (@(posedge clk) req |-> s_nexttime ack);

**Severity**: ERROR

----

.. _FUNC_AVOID_WEAK_UNTIL:

FUNC_AVOID_WEAK_UNTIL
---------------------

Avoid weak ``until``; use ``s_until``.

**Rationale**: The weak ``until`` operator allows non-terminating evaluation —
if the simulation ends before the termination condition is met, the assertion
passes vacuously. Use ``s_until`` (strong until) to guarantee the termination
condition is actually observed within the simulation run.

**Violation**::

    a_hold: assert property (@(posedge clk) busy until ready);

**Correct usage**::

    a_hold: assert property (@(posedge clk) busy s_until ready);

**Severity**: ERROR

----

.. _FUNC_AVOID_WEAK_UNTIL_WITH:

FUNC_AVOID_WEAK_UNTIL_WITH
--------------------------

Avoid weak ``until_with``; use ``s_until_with``.

**Rationale**: Like ``until``, the weak ``until_with`` operator passes vacuously
at simulation end if the termination condition is never reached. Use
``s_until_with`` (strong until_with) to enforce that the endpoint condition
is strictly observed within the simulation run.

**Violation**::

    a_hold: assert property (@(posedge clk) busy until_with ready);

**Correct usage**::

    a_hold: assert property (@(posedge clk) busy s_until_with ready);

**Severity**: ERROR

----

.. _NO_IMPLICATION_PROPERTY:

NO_IMPLICATION_PROPERTY
-----------------------

Avoid logical implication ``->`` in property; use ``|->`` or ``|=>``.

**Rationale**: The ``->`` operator is a combinational logical implication, not
a temporal one. Inside a property it evaluates statically in a single clock
step and does not express sequential behavior. SVA temporal implication
operators ``|->`` (overlapping) and ``|=>`` (non-overlapping) should be used
to express sequential intent correctly.

**Violation**::

    p_bad: property (@(posedge clk) (req -> ack));

**Correct usage**::

    p_ok: property (@(posedge clk) req |-> ack);

**Severity**: ERROR

----

.. _NO_COVER_SEQ:

NO_COVER_SEQ
------------

Avoid ``cover sequence``; use ``cover property`` instead.

**Rationale**: ``cover sequence`` is deprecated in practice and has limited
support across EDA tools. ``cover property`` is the standard, universally
supported form for temporal coverage collection and should always be preferred.

**Violation**::

    c_req: cover sequence (@(posedge clk) req ##1 ack);

**Correct usage**::

    c_req: cover property (@(posedge clk) req ##1 ack);

**Severity**: ERROR

----

.. _PROP_UNUSED_FORMAL_ARG:

PROP_UNUSED_FORMAL_ARG
----------------------

Property has a formal argument that is never used in its body.

**Rationale**: Unused formal arguments indicate dead parameters — either a
check was planned but never implemented, or a refactor left the signature
inconsistent with the body. Callers must still pass values for them, creating
misleading interfaces and dead code.

**Violation**::

    property p_req_ack(input logic clk, input logic unused_sig);
        @(posedge clk) req |-> ack;
    endproperty: p_req_ack

**Correct usage**::

    property p_req_ack(input logic clk);
        @(posedge clk) req |-> ack;
    endproperty: p_req_ack

**Severity**: ERROR

----

.. _PROP_UNUSED_LOCAL_VAR:

PROP_UNUSED_LOCAL_VAR
---------------------

Local variable declared inside a property is never used.

**Rationale**: An unused local variable in a property body is dead code — it
consumes simulator resources on every evaluation thread without contributing
to the check. It typically indicates an incomplete implementation or leftover
from a refactor.

**Violation**::

    property p_data_check;
        int unused_cnt;
        @(posedge clk) valid |-> data != 0;
    endproperty: p_data_check

**Correct usage**::

    property p_data_check;
        @(posedge clk) valid |-> data != 0;
    endproperty: p_data_check

**Severity**: ERROR

----

.. _SEQ_UNUSED_FORMAL_ARG:

SEQ_UNUSED_FORMAL_ARG
---------------------

Sequence has a formal argument that is never used in its body.

**Rationale**: Unused formal arguments in a sequence definition indicate dead
parameters. Callers must still pass values for them, creating misleading
signatures and dead code. Remove unused arguments to keep interfaces clean
and intent clear.

**Violation**::

    sequence s_req(logic clk, logic unused);
        @(posedge clk) ##1 $rose(req);
    endsequence: s_req

**Correct usage**::

    sequence s_req(logic clk);
        @(posedge clk) ##1 $rose(req);
    endsequence: s_req

**Severity**: WARNING

----

.. _DELAY_BEFORE_CHANGED:

DELAY_BEFORE_CHANGED
--------------------

A ``##1`` delay is required immediately before ``$changed``.

**Rationale**: ``$changed(sig)`` compares the current sampled value of ``sig``
with its value on the previous clock edge. Without a preceding ``##1``, the
assertion evaluates on the very first active clock, where there is no
well-defined previous value — the comparison is against an indeterminate initial
state. This causes spurious failures at simulation time zero and immediately
after any reset that re-initialises signal history.

**Violation**::

    p_changed_bad: property (@(posedge clk) req |-> $changed(gnt));

**Correct usage**::

    p_changed_ok: property (@(posedge clk) req |-> ##1 $changed(gnt));

**Severity**: ERROR

----

.. _DELAY_BEFORE_FELL:

DELAY_BEFORE_FELL
-----------------

A ``##1`` delay is required immediately before ``$fell``.

**Rationale**: ``$fell(sig)`` samples the signal on two consecutive clock edges.
Without a preceding ``##1``, the assertion may evaluate before a valid previous
value exists — at time zero or immediately after reset when signal history is
undefined — producing spurious failures that obscure genuine bugs.

**Violation**::

    p_fell_bad: property (@(posedge clk) req |-> $fell(gnt));

**Correct usage**::

    p_fell_ok: property (@(posedge clk) req |-> ##1 $fell(gnt));

**Severity**: ERROR

----

.. _STYLE_NO_CLK_WITHOUT_EDGE:

STYLE_NO_CLK_WITHOUT_EDGE
-------------------------

Avoid ``@(clk)`` as a clocking event; use ``@(posedge clk)`` or ``@(negedge clk)``.

**Rationale**: A clocking event specified as ``@(clk)`` without an explicit
edge qualifier samples the clock on both the rising and falling edges. The
assertion then fires twice per clock period, producing duplicate or conflicting
evaluation results that are almost never the intended behaviour. An explicit
``posedge`` or ``negedge`` qualifier makes the sampling intent unambiguous and
eliminates the double-trigger hazard.

**Violation**::

    p_req_gnt: property (@(clk) req |-> ##1 gnt);

**Correct usage**::

    p_req_gnt: property (@(posedge clk) req |-> ##1 gnt);

**Severity**: ERROR

----

.. _STYLE_NO_IMM_SVA_IN_ALWAYS_COMB:

STYLE_NO_IMM_SVA_IN_ALWAYS_COMB
--------------------------------

Avoid plain immediate assertions inside ``always_comb``; use ``assert final``.

**Rationale**: A plain immediate assertion (``assert (expr)``) placed inside an
``always_comb`` block fires on every delta cycle during combinatorial settling,
not just at the end of the time step. Intermediate glitches on input signals
cause the assertion to trigger before the output has reached its stable value,
producing spurious failures. The deferred form ``assert final`` evaluates only
after all combinatorial activity in the time step has resolved, giving the
correct and stable result.

**Violation**::

    always_comb begin
        assert (a == b) else $error("mismatch");
    end

**Correct usage**::

    always_comb begin
        assert final (a == b) else $error("mismatch");
    end

**Severity**: ERROR

----

.. _STYLE_NO_MIXED_IMPL_OPER:

STYLE_NO_MIXED_IMPL_OPER
------------------------

Do not use ``|->`` and ``|=>`` in the same property.

**Rationale**: Mixing overlapping (``|->``) and non-overlapping (``|=>``)
implication operators in a single property makes the temporal semantics
ambiguous. The consequent of ``|->`` starts in the same clock cycle as the
antecedent, while ``|=>`` starts one cycle later; combining both in the same
property requires the reader to reason about two different reference points
simultaneously, increasing the risk of misinterpretation or misdiagnosis when
the property fails. Each property should express one consistent implication
style.

**Violation**::

    p_mixed: property (@(posedge clk) a |-> (b |=> c));

**Correct usage**::

    p_ab_olap:  property (@(posedge clk) a |-> b);
    p_b_nolap:  property (@(posedge clk) b |=> c);

**Severity**: ERROR

----

.. _STYLE_NO_NESTED_IMPL:

STYLE_NO_NESTED_IMPL
--------------------

Avoid nesting an implication operator inside the consequent of another implication.

**Rationale**: A property of the form ``a |-> (b |-> c)`` places an implication
inside the consequent of an outer implication. When such a property fails, it
is unclear whether the outer or inner implication triggered the violation, and
formal coverage tools may report the inner check as always vacuously true
relative to the outer context. Decomposing into two independent properties
allows the tool to report failures precisely and independently for each check.

**Violation**::

    p_nested: property (@(posedge clk) a |-> (b |-> c));

**Correct usage**::

    p_ab: assert property (@(posedge clk) a |-> b);
    p_bc: assert property (@(posedge clk) b |-> c);

**Severity**: ERROR

----

.. _PERF_NO_UB_REPEAT_IN_ANT:

PERF_NO_UB_REPEAT_IN_ANT
------------------------

Avoid unbounded consecutive repetition ``[*]`` or ``[+]`` in an assertion antecedent.

**Rationale**: The operators ``[*]`` (zero-or-more consecutive matches) and
``[+]`` (one-or-more consecutive matches) in an antecedent force the evaluation
engine to spawn and maintain an unlimited number of concurrent match threads,
one for each possible cycle count. In simulation this causes significant memory
and runtime overhead; in formal tools it leads to state-space explosion that
can render the proof intractable. Replace with a finite upper bound derived
from expected design behaviour.

**Violation**::

    a_req_gnt: assert property (@(posedge clk) req[*] |-> gnt);

**Correct usage**::

    a_req_gnt: assert property (@(posedge clk) req[*1:5] |-> gnt);

**Severity**: ERROR

----

.. _PROP_LOCAL_VAR_NOT_USED_IN_CONSEQ:

PROP_LOCAL_VAR_NOT_USED_IN_CONSEQ
---------------------------------

Local variable captured in the antecedent is never referenced in the consequent.

**Rationale**: A local variable assigned via antecedent capture
(e.g., ``(valid, captured = data)``) is almost always intended to be compared
in the consequent (e.g., ``captured == expected``). If the consequent does not
reference the variable, the captured value is silently discarded and the
intended check is never performed — the property verifies less than the author
expected without producing any warning.

**Violation**::

    property p_data_check;
        int captured;
        @(posedge clk)
            (valid, captured = data) |-> (data > 0);
    endproperty: p_data_check

**Correct usage**::

    property p_data_check;
        int captured;
        @(posedge clk)
            (valid, captured = data) |-> (captured > 0);
    endproperty: p_data_check

**Severity**: ERROR

----

.. _SEQ_UNUSED_LOCAL_VAR:

SEQ_UNUSED_LOCAL_VAR
--------------------

Local variable declared inside a sequence is never used.

**Rationale**: An unused local variable in a sequence body is dead code. The
simulator allocates and tracks it on every evaluation thread without it
contributing anything to the check. This wastes resources and typically
indicates an incomplete implementation — a variable was declared in anticipation
of a check that was never written — or a remnant from refactoring.

**Violation**::

    sequence seq_check;
        int unused_cnt;
        valid ##1 (data > 0);
    endsequence

**Correct usage**::

    sequence seq_check;
        valid ##1 (data > 0);
    endsequence

**Severity**: ERROR

----

.. _STYLE_THROUGHOUT_RHS_BOOL:

STYLE_THROUGHOUT_RHS_BOOL
-------------------------

RHS of ``throughout`` must be a multi-cycle sequence expression, not a plain boolean.

**Rationale**: The ``throughout`` operator has the form
``boolean_cond throughout sequence_expr``. Its purpose is to assert that a
condition holds continuously across every clock cycle spanned by a multi-cycle
sequence on the right-hand side. When the RHS is a plain boolean signal rather
than a sequence with cycle delays or repetitions, ``throughout`` degenerates
to a single-cycle evaluation that is semantically identical to a simple
conjunction — the temporal meaning of ``throughout`` is lost, and the intent
of the property becomes misleading to readers.

**Violation**::

    p_valid_throughout: property (@(posedge clk)
        valid throughout ack);

**Correct usage**::

    p_valid_throughout: property (@(posedge clk)
        valid throughout (req ##[1:5] ack));

**Severity**: ERROR

----

.. _PROP_UNUSED_PROPERTY:

PROP_UNUSED_PROPERTY
--------------------

Property declared but never referenced by any assertion, assumption, or cover directive.

**Rationale**: A property that is declared but never bound to an
``assert property``, ``assume property``, or ``cover property`` statement
contributes zero verification value — it is never evaluated by the tool.
This typically indicates either dead code left over from a refactoring, or an
incomplete implementation where the binding statement was written but then
deleted, or was simply forgotten. Either way, the property must be either
instantiated or removed.

**Violation**::

    property p_req_gnt;
        @(posedge clk) req |-> ##1 gnt;
    endproperty: p_req_gnt
    // No assert/assume/cover statement references p_req_gnt

**Correct usage**::

    property p_req_gnt;
        @(posedge clk) req |-> ##1 gnt;
    endproperty: p_req_gnt
    a_req_gnt: assert property (p_req_gnt);

**Severity**: ERROR

----

.. _SEQ_UNUSED_SEQUENCE:

SEQ_UNUSED_SEQUENCE
-------------------

Sequence declared but never referenced by any property or assertion.

**Rationale**: A sequence that is declared but never instantiated inside a
property, assertion, or cover directive is never evaluated and provides no
verification coverage. It is either dead code from a refactor, or an
incomplete implementation where the property that was supposed to use the
sequence was never written. Unused sequences should be removed to keep the
SVA codebase lean and free of misleading dead code.

**Violation**::

    sequence seq_req_gnt;
        req ##1 gnt;
    endsequence
    // No property or assertion references seq_req_gnt

**Correct usage**::

    sequence seq_req_gnt;
        req ##1 gnt;
    endsequence

    property p_req_gnt;
        @(posedge clk) seq_req_gnt;
    endproperty: p_req_gnt

    a_req_gnt: assert property (p_req_gnt);

**Severity**: ERROR
