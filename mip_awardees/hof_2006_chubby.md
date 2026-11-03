# The Chubby lock service for loosely-coupled distributed systems

**Summary by:** GPT 6 Astra

**Author:** Mike Burrows

**Source:** OSDI 2006; SIGOPS Hall of Fame Award 2017

**Link:** https://www.usenix.org/legacy/event/osdi06/tech/burrows.html

## Key insight

A replicated service with a familiar file-and-lock interface can provide coordination without asking every application to implement consensus. Lock ownership must also be checked at the resource being protected, because delayed requests can outlive their owner's lock.

## Basic idea

Chubby supplies coarse-grained advisory locks [1] and small files backed by a replicated state machine [2]. Clients maintain sessions with leases [3], cache reads, and receive invalidations before conflicting modifications complete. An application can elect a primary by acquiring an exclusive lock, then pass a sequencer [4] with protected operations. Replication keeps the coordination service consistent, while sequencer checks let cooperating resource servers reject operations from obsolete lock holders.

## Illustrative example

**Acquire leadership.** Two indexing workers, A and B, compete for a lock associated with `/jobs/indexer`. A acquires it and obtains a sequencer containing the lock identity, mode, and acquisition generation. A includes this sequencer in requests to a storage server that accepts writes only from the current indexer.

**Handle delay.** A sends an update that stalls in the network. Its Chubby session expires, and B eventually acquires the lock with a newer generation. B sends an update carrying the new sequencer. The storage server validates it against Chubby state or records the newer generation under the checking scheme it supports.

When A's old request finally arrives, a proper sequencer check rejects it. Merely asking A to stop when its lease expires is insufficient: A may be paused, disconnected, or have already sent the request. An advisory lock also does not automatically prevent a client from writing the storage server; the server must participate in enforcement.

**Keep cached metadata coherent.** Suppose A cached a small configuration file stored in Chubby. Before a conflicting update completes, the master sends invalidations to relevant clients. It waits until each client acknowledges invalidation or its cache lease expires. A client that cannot establish valid cached state must report uncertainty or failure rather than return the stale value as current.

**Failure boundary.** Chubby's servers use consensus to agree on durable state and select a master. A session can survive some master changes, but loss of the required communication can delay progress. For legacy services that cannot check sequencers, Chubby offers a lock-delay after an inaccessible holder loses a lock. That delay reduces common stale-request hazards but is not a proof against arbitrarily delayed requests.

## Concepts and terms

**[1] Coarse-grained advisory lock.** A lock normally held for relatively long coordination tasks, such as choosing a primary. It protects another resource only when clients and that resource's server honor the lock protocol.

**[2] Replicated state machine.** Servers execute an agreed sequence of operations on matching state. Chubby uses Paxos internally; clients see a higher-level interface rather than implementing the agreement protocol themselves.

**[3] Session and lease.** A session associates client state and locks with the service. A lease promises that the session will not be terminated unilaterally before a specified timeout; renewal and invalidation handling maintain its validity.

**[4] Sequencer.** Evidence identifying a particular acquisition of a lock, including its generation and mode. A recipient uses it to detect stale authority on a protected request.
