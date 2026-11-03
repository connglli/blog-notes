# Why Do Computers Stop and What Can Be Done About It?

**Summary by:** GPT 6 Astra

**Author:** Jim Gray

**Source:** Tandem Technical Report 85.7, 1985, revised November 1985; SIGOPS Hall of Fame Award 2011

**Link:** https://www.hpl.hp.com/techreports/tandem/TR-85.7.html

## Key insight

Availability depends on recovering quickly from component failures, including software and administration failures, not merely making hardware more reliable. Process isolation, restart, and transactional recovery can work together to keep a service operating despite some faults.

## Basic idea

Gray studies failures of a fault-tolerant system and distinguishes availability [1] from simply avoiding individual component failures. He advocates fail-fast modules [2] whose failures are contained and detected, with process pairs [3] providing takeover. Re-execution can avoid some transient software failures, termed Heisenbugs [4], when the backup does not reproduce precisely the same failing state. Transactions [5] remove incomplete effects so a replacement process can restart useful work from a known boundary. This is a conditional recovery strategy, not a claim that restarting fixes every defect or that replicas fail independently by construction.

## Illustrative example

**Contain a failure.** An order service runs as a primary process with a backup and uses transactional storage. Request R reserves one item and records the order. The primary updates its transaction's tentative state, then detects an internal consistency failure before commit and stops. It does not keep processing requests with state it knows is invalid.

**Recover a boundary.** The transaction mechanism aborts R's incomplete changes, including the tentative reservation. The backup resumes the service's session and retries R from its original input. It does not need an exact checkpoint of every temporary variable if transactional recovery reconstructs a suitable starting state.

**Avoid reproducing the fault when possible.** Suppose the failure depended on a rare scheduling interaction or corrupted transient process state. A fresh execution can complete even when both processes run the same software. If instead the request deterministically triggers a missing bounds check, repeating it can fail again. Running replicas in exact lockstep can also reproduce the same problematic state, so redundancy alone does not establish software-fault independence.

**Respect completed work.** If R had committed before the process stopped, its durable outcome must be distinguished from an uncommitted attempt. The surrounding transaction and message protocol must prevent a retry from silently reserving a second item. An external effect that cannot be rolled back, such as an uncontrolled physical action, needs its own recovery contract.

**Measure service availability.** In a simplified repair model, availability is `MTBF / (MTBF + MTTR)`. Reducing service interruption from ten minutes to one second can materially improve availability even if component failures occur equally often. Those numbers illustrate the formula, not the paper's measurements. Operator errors and common infrastructure failures can affect both copies and must be considered separately.

## Concepts and terms

**[1] Availability.** The ability to provide the required service when needed. MTBF is mean time between failures and MTTR mean time to repair; their simple ratio model assumes the corresponding alternating operational and repair periods.

**[2] Fail-fast module.** A component intended to detect unacceptable state and stop rather than continue emitting incorrect results. Detection and containment are required mechanisms, not automatic consequences of using processes.

**[3] Process pair.** A primary and backup arranged for takeover. Different designs transfer different amounts of state; persistent process pairs rely heavily on transaction recovery when restarting work.

**[4] Heisenbug.** A software fault whose manifestation depends on circumstances that can disappear on retry or observation, contrasted with a consistently reproducible Bohrbug.

**[5] Transaction.** A unit of work with an atomic outcome and durable committed effects, allowing incomplete changes to be undone before re-execution.
