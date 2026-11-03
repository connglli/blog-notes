# Managing Update Conflicts in Bayou, a Weakly Connected Replicated Storage System

**Summary by:** GPT 6 Astra

**Author:** Douglas B. Terry, Marvin M. Theimer, Karin Petersen, Alan J. Demers, Mike J. Spreitzer, and Carl H. Hauser

**Source:** SOSP 1995; SIGOPS Hall of Fame Award 2015

**Link:** https://doi.org/10.1145/224057.224070

## Key insight

Disconnected replicas need more than a rule for choosing the latest bytes. Each update can carry its own test for conflicts and a deterministic procedure for resolving them according to the application's meaning.

## Basic idea

Bayou accepts writes at available replicas and propagates them through anti-entropy [1]. Each write contains a dependency check [2] and a merge procedure [3], which determine its effect against the replica state at execution time. Tentative writes [4] may be undone and replayed when replicas learn a different ordering. A primary assigns committed order [5], and replicas executing the same ordered writes converge because checking and merging are deterministic. Applications can distinguish tentative results from stable ones instead of treating every local success as final.

## Illustrative example

**Submit.** Two disconnected replicas manage a small shared equipment schedule. A client at replica A requests microscope M at 10:00; another at B requests the same slot. Each write checks whether that reservation is free and carries a fallback procedure that tries 11:00, then records failure if neither slot is free. The choices and search order are embedded in the write rather than taken from a local wall clock.

Each replica initially sees an empty schedule and tentatively grants 10:00. This is allowed: the replicas have different known write sets, and clients must not mistake a tentative reservation for a final commitment.

**Exchange and reorder.** Anti-entropy transfers the writes. Suppose A's write precedes B's in the agreed tentative order. A executes first and occupies 10:00; B's dependency check then fails, so its merge procedure chooses 11:00. B's replica must undo its earlier tentative execution and replay the relevant suffix in the proper order. Re-running only the newly received operation would leave inconsistent results.

**Commit.** The designated primary assigns final commit sequence positions. Committed writes precede tentative writes, so learning a commitment can require further replay. Once both reservations occupy a stable committed prefix, later writes cannot be inserted before them. A client can query stability before relying on a reservation as confirmed.

**Contract.** If replicas receive the same writes and apply the same ordering and deterministic procedures, their database contents agree. A merge procedure cannot consult an uncontrolled random value, local clock, or server identity and still satisfy this argument. A partition can postpone final commitment without preventing tentative local use; it cannot guarantee that every user's first-choice reservation survives reconciliation.

## Concepts and terms

**[1] Anti-entropy.** Pairwise exchange of missing writes between replicas. Eventual propagation requires sufficient later connectivity; the system cannot impose a universal delivery-time bound.

**[2] Dependency check.** An application-supplied query and expected result evaluated before applying a write. It detects semantic conflicts that need not be simple writes to the same record.

**[3] Merge procedure.** Code carried with a write that computes a revised update when its dependency check fails. Its allowed inputs and resource limits must produce deterministic behavior across replicas.

**[4] Tentative write.** An accepted update whose order or effect can still change as other updates arrive. The log and database support undoing and re-executing these operations.

**[5] Committed order.** The final ordering assigned by a primary. A stable write has no possible newly arriving predecessor; its execution therefore need not be revised again.
