# Viewstamped Replication: A New Primary Copy Method to Support Highly-Available Distributed Systems

**Summary by:** GPT 6 Astra

**Author:** Brian M. Oki and Barbara H. Liskov

**Source:** PODC 1988; SIGOPS Hall of Fame Award 2012

**Link:** https://doi.org/10.1145/62546.62549

## Key insight

A reply from a primary need not mean that a transaction's entire history will survive failover. Viewstamps record which events occurred, so transaction preparation can verify their survival and require enough replication before allowing commitment.

## Basic idea

Viewstamped replication organizes each module into a primary and backup cohorts [1] operating in a view [2]. The primary executes remote calls, assigns viewstamps [3], and propagates event records to backups. Two-phase commit [4] checks that a transaction's required events survive and forces them to a majority before commitment. View changes preserve majority-known history and establish a new primary, while transactions whose required events were lost must abort. This is the paper's transactional replication design, not merely a renamed presentation of a later state-machine-replication protocol.

## Illustrative example

**Execute a call.** A replicated inventory module has cohorts A, B, and C; A is primary in view 7. A transaction requests that item `lens` be reserved. A executes the call, retains its tentative changes under transaction control, appends the relevant event record, and returns a viewstamp such as `(7, 12)`. The transaction accumulates this dependency with those from other calls.

**Fail before replication.** Suppose A fails before B or C receives event 12. B and C can form the majority needed to install view 8, but their surviving history does not include the event. When the transaction prepares, its dependency information includes `(7, 12)`. The replacement primary detects that this event did not survive and refuses preparation. A successful individual call was therefore not permission to commit a transaction whose effects vanished.

**Commit a surviving history.** Alternatively, suppose B received the event before A failed. The view-change protocol gathers and transfers the required state for the new view. During preparation, a compatible history permits the primary to force the necessary records to enough backups that a majority of the configuration knows them. Only then does it report that the participant is prepared.

The coordinator collects participant decisions and replicates its commit decision as required before distributing the outcome. A later view change must retain events known to a majority because its own majority intersects that set. Cohorts use view identifiers to reject requests addressed to an obsolete view and unique call identifiers to avoid repeating a call merely because a message was retried.

The argument assumes the protocol's crash and communication model and enough functioning cohorts to form a view. A minority cannot independently become a usable competing primary. Losing a majority of the relevant state, or failing the location service needed to discover groups, falls outside an unconditional availability claim.

## Concepts and terms

**[1] Cohort.** One replica of a module's state. A configuration names its replica set; one cohort is primary and the others maintain backup information.

**[2] View.** A majority-containing group of communicating cohorts together with its designated primary and an ordered view identifier. A view change installs a new such arrangement.

**[3] Viewstamp.** A pair combining a view identifier and an event timestamp within that view. Histories use these pairs to determine which events from earlier views survived.

**[4] Two-phase commit.** Transaction coordination in which participants first prepare and a coordinator then chooses the common outcome. Here preparation includes checking viewstamp dependencies and forcing their replication, not just acquiring local locks.
