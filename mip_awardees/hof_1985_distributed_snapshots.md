# Distributed Snapshots: Determining Global States of a Distributed System

**Summary by:** GPT 6 Astra

**Author:** K. Mani Chandy and Leslie Lamport

**Source:** ACM Transactions on Computer Systems 3(1), 1985; SIGOPS Hall of Fame Award 2013; Dijkstra Prize in Distributed Computing 2014

**Link:** https://doi.org/10.1145/214451.214456

## Key insight

A global state consists of both process states and messages in transit. Markers can separate pre-snapshot from post-snapshot traffic without stopping the underlying computation or requiring a shared clock.

## Basic idea

The algorithm records a consistent global snapshot [1] in a system with reliable FIFO channels [2]. A process records its own state and sends a marker [3] on every outgoing channel before further ordinary messages. On its first marker, a process records its state and propagates markers; on other incoming channels it records messages received until their markers arrive. These recorded messages form the channel states. The resulting snapshot supports detection of stable properties [4], although it need not equal the state at one particular wall-clock instant of the observed run.

## Illustrative example

**Setup.** Processes A and B hold 6 and 4 tokens, respectively. A sends two tokens to B, subtracting them locally, but that transfer is still in transit. Assume reliable ordered channels in both directions and eventual delivery.

**Start at B.** B records its local count as 4 and sends a marker to A. B starts recording ordinary messages arriving from A because it has not yet received A's marker. A receives B's marker while holding 4 tokens, records that state, records the B-to-A channel as empty, and sends its marker to B before sending further ordinary messages.

**Record the channel.** The earlier two-token transfer reaches B before A's marker, because A sent the transfer first and the channel is FIFO. B may apply it to its live state, but also records it as part of the A-to-B channel snapshot. When A's marker arrives, B stops recording that channel.

The snapshot contains A's recorded 4 tokens, B's recorded 4 tokens, and 2 tokens in transit: the original total of 10. Simply adding the two recorded process states would incorrectly suggest that tokens disappeared. Later ordinary transfers do not contaminate this channel state because their marker boundary separates them.

**Generalize.** For a process with several incoming channels, the first marker causes local recording; subsequent markers close the recordings for their own channels. A process's local state is recorded once for a snapshot instance. Markers must be sent after that local record and before post-record ordinary messages on each outgoing channel.

A stable condition found true in the recorded state remains true after the snapshot completes under the paper's model. Arbitrary transient conditions need more careful interpretation. Lost messages, reordered channels, process crashes during the protocol, or a marker that cannot reach a participant require additional machinery not supplied by this basic algorithm.

## Concepts and terms

**[1] Consistent global snapshot.** Local process states plus channel contents forming a causally possible state: it cannot record a receive without the corresponding send. It can correspond to a reordering of independent events rather than an observed simultaneous instant.

**[2] FIFO channel.** A communication channel that delivers messages in send order. The original algorithm additionally assumes error-free delivery with finite delay and adequate buffering.

**[3] Marker.** A control message delimiting the sender's recorded state from its later ordinary traffic on one channel. It changes snapshot bookkeeping, not the application computation.

**[4] Stable property.** A predicate that remains true once it becomes true during the modeled computation, such as termination when no new work can be introduced.
