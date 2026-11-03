# Spanner: Google's Globally-Distributed Database

**Summary by:** GPT 6 Astra

**Author:** James C. Corbett, Jeffrey Dean, Michael Epstein, Andrew Fikes, Christopher Frost, JJ Furman, Sanjay Ghemawat, Andrey Gubarev, Christopher Heiser, Peter Hochschild, Wilson Hsieh, Sebastian Kanthak, Eugene Kogan, Hongyi Li, Alexander Lloyd, Sergey Melnik, David Mwaura, David Nagle, Sean Quinlan, Rajesh Rao, Lindsay Rolig, Yasushi Saito, Michal Szymaniak, Christopher Taylor, Ruth Wang, and Dale Woodford

**Source:** OSDI 2012; SIGOPS Hall of Fame Award 2022

**Link:** https://www.usenix.org/conference/osdi12/technical-sessions/presentation/corbett

## Key insight

A clock API that exposes a reliable uncertainty interval lets transactions wait until their timestamps are definitely in the past. Combined with locking and replicated commit, this aligns transaction order with real-time order across data centers.

## Basic idea

Spanner partitions data among Paxos groups [1] and coordinates transactions spanning groups with two-phase commit [2]. TrueTime [3] returns an interval containing the current absolute time rather than pretending to know an exact instant. A transaction chooses a sufficiently large commit timestamp, records its decision durably, and performs commit wait [4] before exposing the result. Together with concurrency control, this provides external consistency [5]; clock uncertainty affects waiting time rather than allowing the database to disregard the ordering contract.

## Illustrative example

**Setup.** Account `elm` is stored in replica group A and account `oak` in group B. A transfer subtracts 7 from `elm` and adds 7 to `oak`. Each group has a leader that acquires the required locks; each group's durable records are replicated through its own Paxos protocol. Assume clocks satisfy TrueTime's interval guarantee and enough replicas remain reachable to commit.

**Prepare.** Choose A as the transaction coordinator. B acquires its write lock, chooses a prepare timestamp greater than its earlier assigned timestamps, replicates a prepare record, and sends the timestamp to A. A also acquires its write locks. The transaction cannot simply commit at one group and independently hope that the other succeeds.

**Timestamp and wait.** Suppose B's prepare timestamp is 100, A's previous timestamps are below 100, and the relevant TrueTime upper bound is 103. A can choose commit timestamp 104, respecting those bounds, and replicate its commit decision. Before making the result visible, it waits until `TT.now().earliest > 104`. An interval of `[102,106]` is insufficient; `[105,109]` is sufficient. The timestamp is then definitely earlier than the real completion time.

**Apply.** The coordinator sends the outcome and timestamp to the other participant and the client. Participants record the outcome, apply the writes at the common timestamp, and release their locks. A transaction that starts after this transfer returns must receive a later serialization position. Concurrent transactions need not be ordered by their wall-clock start times.

If uncertainty expands, the wait can lengthen. If the necessary replica quorum or transaction participants cannot communicate, progress can stop. TrueTime does not make a network partition disappear or replace the replication and atomic-commit protocols.

## Concepts and terms

**[1] Paxos group.** Replicas that agree on a sequence of durable updates using intersecting quorums. A leader coordinates ordinary writes; unavailable quorums can prevent progress without authorizing conflicting committed values.

**[2] Two-phase commit.** Participants first promise they can commit and retain the necessary state; a coordinator then records and distributes a common commit or abort decision. It provides atomic outcome across groups, while replication protects individual records.

**[3] TrueTime.** An API whose `now` operation returns earliest and latest bounds on absolute time. Its correctness depends on those bounds actually enclosing the time of the call.

**[4] Commit wait.** Delaying visibility until the earliest possible current time exceeds the chosen commit timestamp.

**[5] External consistency.** Transactions behave as if executed in a serial order that respects real-time precedence: if one finishes before another starts, it precedes the other in that order.
