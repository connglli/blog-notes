# Generalized FLP Impossibility Result for t-Resilient Asynchronous Computations

**Summary by:** GPT 6 Astra

**Author:** Elizabeth Borowsky, Eli Gafni

**Source:** STOC 1993; Edsger W. Dijkstra Prize in Distributed Computing, 2017

**Link:** https://doi.org/10.1145/167088.167119

## Key insight

Allowing k different decision values does not permit deterministic asynchronous agreement to tolerate k crashes using only read/write shared memory. A simulation converts that resilience requirement into an impossible wait-free problem on k+1 processes.

## Basic idea

In k-set consensus [1], processes must choose proposed values while producing at most k distinct outputs. The paper establishes impossibility with k crash failures and no timing bounds, extending the single-failure consensus result. It first proves the wait-free [2] case using the structure of local views produced by immediate atomic snapshots [3]. A simulation based on restricted agreement [4] lets k+1 simulators execute an n-process k-resilient protocol while each simulator failure blocks at most one simulated process. This reduces the general case to the wait-free impossibility.

## Illustrative example

**Assume a solution.** Suppose five processes could solve two-set consensus despite two crashes. Three real simulators, Ash, Birch, and Cedar, have inputs 0, 1, and 2. They jointly execute five virtual processes, agreeing on each virtual input as one of the real inputs. Every virtual process's history is recorded in shared memory.

**Agree on steps.** A virtual read might see different memory states when different simulators attempt it. Give that read its own agreement instance. Each simulator posts a proposed result, obtains an immediate-snapshot participant set, and publishes that set. One sufficient completion condition is that every member of some published set has published its own set. Choose the proposal of the lowest-numbered member of the smallest such participant set. The nested sets and immediate-snapshot condition prevent a conflicting smaller set from appearing later.

**Contain a failure.** A simulator finishes the publication phase before entering another agreement instance, but can suspend an unfinished waiting phase and work on another virtual process. If Ash crashes during publication for virtual process 1, and Birch does likewise for process 2, at most those two virtual processes remain blocked. Cedar continues simulating the other three. The assumed two-crash-tolerant protocol must let them decide; Cedar adopts a completed virtual decision. The same rule lets every surviving real simulator terminate and preserves the bound of two distinct outputs.

**Reach the contradiction.** This would solve wait-free two-set consensus among three real processes. Their possible local views can be represented by a subdivided input triangle. Validity forces each boundary edge to use only its two participating inputs. Sperner's lemma [5] forces a small triangle with all three decision labels, representing a compatible execution with three outputs. That contradicts two-set consensus. The example shows the reduction's failure accounting and the three-process geometric obstruction, rather than replacing the general proof.

## Concepts and terms

**[1] k-set consensus.** Every nonfailed participant eventually returns a proposed value, and at most k values occur across decisions. A k-resilient algorithm must satisfy this with up to k crashes.

**[2] Wait-free.** Each nonfailed process finishes after finitely many of its own steps, regardless of other processes' speeds or failures.

**[3] Immediate atomic snapshot.** A combined publication-and-observation abstraction implementable with read/write memory: a process sees itself; returned participant sets are nested; if p appears in q's set, p's set is contained in q's set.

**[4] Restricted agreement.** Agreement with a wait-free proposal-publication phase followed by a possibly blocking resolution phase. Failure during publication can block that instance; failure after publication cannot.

**[5] Sperner's lemma.** A boundary-respecting labeling of a subdivided simplex contains a fully labeled small simplex. In the triangle case, compatible local decisions must somewhere use all three corner labels.
