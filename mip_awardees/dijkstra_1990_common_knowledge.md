# Knowledge and common knowledge in a distributed environment

**Summary by:** GPT 6 Astra

**Author:** Joseph Y. Halpern and Yoram Moses

**Source:** Journal of the ACM 37(3), 1990; Edsger W. Dijkstra Prize in Distributed Computing 2009.

**Link:** https://doi.org/10.1145/79147.79161

## Key insight

Knowing a fact, knowing that others know it, and knowing that everyone knows that everyone knows it are different protocol states. Coordination requirements can be analyzed by identifying which level of shared knowledge they require.

## Basic idea

The framework models an agent's knowledge [1] using global situations indistinguishable [2] from its local observations. Everyone-knows [3] combines individual knowledge, while common knowledge [4] requires arbitrarily nested everyone-knows statements. The paper connects these notions to coordinated actions and shows why communication uncertainty prevents new common knowledge in important models. Weaker timed or eventual variants capture coordination goals that do not require perfectly simultaneous knowledge.

## Illustrative example

**Fact and message.** Ada learns that a valve is closed and sends this fact to Ben over a channel where a message might be lost. Assume truthful agents and no other source of information about the valve.

If Ben receives the message, he knows the valve is closed. Ada also knows it, but cannot distinguish this run from one where her message was lost. Thus Ada does not yet know that Ben knows it.

**Acknowledgment.** Ben sends an acknowledgment. When Ada receives it, Ada knows that Ben knows the valve is closed. Ben, however, cannot distinguish that run from one in which his acknowledgment was lost. He does not know that Ada knows he received the original message.

Another acknowledgment raises the nesting depth again but leaves uncertainty about the newest message's receipt. A finite exchange does not remove every such uncertainty under this channel model.

**Model-checking view.** Represent each possible delivery history as a point containing both agents' local histories. Ada's indistinguishability relation connects points with the same Ada history; Ben's does the same for Ben. Ada knows a predicate only if it is true at every point in her class.

To check common knowledge, follow any finite chain of either agent's indistinguishability links and require the predicate at every reachable point. This can connect the actual run to histories missing progressively earlier messages. Checking only the actual run or only one agent's class misses the group condition.

**Coordination boundary.** This argument concerns common knowledge and the associated perfectly coordinated actions, not a claim that no useful agreement or eventual action is possible. Known timing bounds, public events, or weaker coordination requirements change what agents can establish.

## Concepts and terms

**[1] Knowledge.** An agent knows a fact when it holds in every global situation compatible with that agent's local state, given the system model.

**[2] Indistinguishability.** Two global situations are indistinguishable to an agent when its local observations do not distinguish them. Different agents can have different equivalence classes.

**[3] Everyone-knows.** A group operator requiring each member individually to know a fact. Applying it twice additionally requires everyone to know that everyone knows the fact.

**[4] Common knowledge.** A fact is common knowledge when every finite nesting of the everyone-knows operator holds. Equivalently, the fact holds at every point reachable through any finite chain of group members' indistinguishability relations.

