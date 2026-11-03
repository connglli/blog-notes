# Disconnected Operation in the Coda File System

**Summary by:** GPT 6 Astra

**Author:** James J. Kistler and M. Satyanarayanan

**Source:** ACM Transactions on Computer Systems 10(1), 1992; SIGOPS Hall of Fame Award 2015

**Link:** https://doi.org/10.1145/146941.146942

## Key insight

A client's cache can provide availability as well as speed. If it contains the files needed for useful work, the client can operate independently and later reconcile its logged changes with the servers.

## Basic idea

Coda's client cache manager, Venus, moves between hoarding [1], emulation [2], and reintegration [3]. While connected, it combines user priorities with observed use to keep useful whole files and directory information cached. During disconnection, it serves available data locally and records mutations in a replay log [4]. Upon reconnection, servers check and replay those changes; conflicting updates may require repair rather than being silently overwritten. This optimistic replication [5] favors continued work but cannot make an uncached file available without a server.

## Illustrative example

**Hoard.** A user plans to edit `/project/report` offline. The hoard profile names that file and relevant supporting paths. Venus periodically reconciles priorities, validates cached objects, and fetches what the cache should contain. Hoarding must include directory information needed to resolve the name, not just an isolated file's bytes.

**Emulate.** The laptop loses access to every available server for the volume. Venus serves the cached report. The user changes two paragraphs and closes it twice. Rather than retaining every individual write, the replay log can keep the final store operation and current file contents needed to reproduce the resulting state. Locally modified objects are protected against ordinary cache eviction before reintegration.

If the user opens an uncached appendix, the operation fails: the client cannot manufacture missing data. Whole-file caching simplifies this case because a successfully cached file is not missing arbitrary interior blocks during later reads.

**Reintegrate.** The connection returns. Venus presents the logged operations and version information to the server. If the server's report has not changed incompatibly, it can install the client's final contents and return to connected operation. If another user independently modified the report, validation detects the conflict. The system preserves information for repair instead of treating the laptop's old cache as authoritative.

The cached client copy is not equivalent to a professionally managed server replica. Its disk can fail, its user can turn it off, and disconnected updates lack the normal server replication until successful reintegration. The model therefore provides useful local service during a partition, not globally serializable editing or guaranteed durability against loss of the disconnected client.

## Concepts and terms

**[1] Hoarding.** Maintaining a prioritized cache in anticipation of disconnection. Explicit user preferences and ordinary reference activity jointly influence what remains resident.

**[2] Emulation.** Having the client cache manager act as the local file-service provider while servers are unreachable. Requests succeed only when the required cached state and local resources exist.

**[3] Reintegration.** Validating and replaying disconnected changes against server state. Success propagates updates; conflicts are exposed for resolution instead of assumed away.

**[4] Replay log.** A compact record of mutating operations sufficient to reproduce disconnected changes. Redundant or canceling operations can be removed when doing so preserves their net effect.

**[5] Optimistic replication.** Allowing updates without first coordinating with every other copy, then detecting incompatible histories during reconciliation. It accepts the possibility of later conflict to preserve availability.
