# The Part-Time Parliament

**Summary by:** GPT 6 Astra

**Author:** Leslie Lamport

**Source:** ACM Transactions on Computer Systems 16(2), 1998; SIGOPS Hall of Fame Award 2012

**Link:** https://doi.org/10.1145/279227.279229

## Key insight

Intersecting voting groups are insufficient unless a later proposer discovers and preserves earlier voting history. Numbered ballots and durable promises allow agreement to remain safe even when messages are delayed and participants repeatedly stop and restart.

## Basic idea

Paxos chooses a value through ballots [1] whose quorums [2] intersect. A proposer first obtains promises [3] and each voter's latest accepted value, then proposes the value attached to the highest earlier accepted ballot, or a new value if none exists. A quorum accepting the proposal chooses that value, even if the proposer fails before announcing success. Repeating agreement for numbered log positions [4] produces a consistent sequence of commands. Safety does not require timely messages, but progress requires a sufficiently stable participating majority and effective leader coordination.

## Illustrative example

**Choose without announcing.** Three voters A, B, and C agree on one log position. A proposer obtains promises for ballot 4 from A and B; neither reports an earlier vote. It proposes `set mode = quiet`. Both accept, so the value is chosen by a majority. The proposer then fails before telling C or the client.

**Recover knowledge.** Another proposer starts ballot 9 and contacts B and C. Both promise not to accept lower-numbered ballots. B reports that it accepted `quiet` in ballot 4; C reports no accepted value. The proposer cannot choose `loud` just because it has not received a success announcement. It must carry forward the value from the highest reported accepted ballot, which is `quiet`.

**Accept again.** B and C accept `quiet` under ballot 9. The new proposer can announce the decision. The two choosing majorities intersect at B, whose durable history connects the ballots. If an old ballot-4 proposal reaches C after its ballot-9 promise, C rejects it rather than acting on message arrival order.

**Build a sequence.** The same reasoning applies separately to each numbered log slot. A leader coordinates filling slots and learns prior decisions so commands can be executed in their numbered order. The agreement primitive does not itself make a client's retried application request occur exactly once; request identifiers and service-level handling are separate concerns.

If A and B stop permanently, C alone must not choose a contradictory replacement. Likewise, competing proposers can repeatedly preempt one another without violating safety. Persisting promises and accepted votes across restart is essential: a voter that forgets its history can break the intersection argument.

## Concepts and terms

**[1] Ballot.** An attempt to choose a value under a unique ordered number. Numbers order authority and voting constraints, not the wall-clock arrival of network messages.

**[2] Quorum.** A set of voters sufficient to choose a value. The paper uses majority-style intersecting sets so any later choosing attempt consults at least one participant from an earlier successful set.

**[3] Promise and accepted vote.** Durable voter state recording the minimum ballot it will entertain and its latest accepted ballot/value. The first phase reads this state and restricts what the proposer may safely propose.

**[4] Numbered log position.** One independently agreed entry in a replicated sequence. Replicas can learn entries at different times but must not learn different chosen values for the same position.
