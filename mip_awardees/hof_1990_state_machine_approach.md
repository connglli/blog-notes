# Implementing Fault-Tolerant Services Using the State Machine Approach: A Tutorial

**Summary by:** GPT 6 Astra

**Author:** Fred B. Schneider

**Source:** ACM Computing Surveys 22(4), 1990; SIGOPS Hall of Fame Award 2007

**Link:** https://doi.org/10.1145/98163.98167

## Key insight

Replicas remain equivalent when they start alike and execute the same deterministic commands in the same order. Fault tolerance then depends on establishing that shared request history and selecting trustworthy outputs under an explicit failure model.

## Basic idea

The state-machine approach [1] represents a service as deterministic commands over state. Replicas require agreement [2] about which requests to process and ordering [3] that makes their executions match. A request becomes executable only when its position is stable [4], rather than merely because it is the smallest request received so far. Output handling and replica counts depend on the failure model [5], and nondeterministic information must be supplied as coordinated input. The tutorial separates these obligations rather than identifying replication with simply running several copies of the same program.

## Illustrative example

**Define deterministic commands.** A service holds integer `balance = 10`. Command `add(4)` raises it by 4; command `spend(12)` succeeds and subtracts 12 only when the balance is at least 12. Every correct replica begins in the same state and executes each command atomically relative to other commands.

**Order requests.** If all replicas execute `add(4)` before `spend(12)`, the spend succeeds and the final balance is 2. In the opposite order, the spend fails and the final balance is 14. Receiving both requests is therefore insufficient; the order affects observable results.

**Wait for stability.** An agreement-and-ordering layer assigns the add to position 20 and the spend to 21. A replica that receives 21 first cannot immediately execute it. It waits until it knows the earlier required history and that no missing request can precede the next selected request. Once it applies the same stable sequence as its peers, determinism gives the same results.

**Control outside inputs.** Suppose the service also expires a reservation according to time. Having each replica read its own clock inside the command can make the results differ. Instead, an appropriately generated time observation must enter as part of the coordinated request history, or the design must otherwise establish equivalent behavior. Determinism is an interface requirement, not a property automatically supplied by a programming language.

**Handle faults.** With fail-stop replicas, a surviving replica's result is not arbitrarily fabricated. With Byzantine replicas, output selection must tolerate incorrect answers, and the agreement protocol must tolerate its own adversarial behaviors. Counting enough identical outputs does not by itself solve dissemination or ordering. The necessary replicas and assumptions depend on the chosen communication, authentication, and failure model.

Recovery must initialize a replacement from a consistent state and corresponding request position before it participates. A copied state without the matching history boundary risks omitting or repeating commands.

## Concepts and terms

**[1] State-machine approach.** Replicating a service whose output and next state are determined by its initial state and request sequence, independent of uncontrolled local events.

**[2] Agreement.** Ensuring correct replicas obtain the same relevant requests despite failures during dissemination. Reliable delivery to one replica is not sufficient.

**[3] Ordering.** Ensuring correct replicas process requests in a common order respecting the required causal constraints.

**[4] Stability.** Knowledge that no later arrival can precede a request in the chosen order. It justifies executing that request rather than continuing to wait.

**[5] Failure model.** The behaviors the design must tolerate. Fail-stop components cease operating detectably; Byzantine components can behave arbitrarily. Replication requirements and output rules differ accordingly.
