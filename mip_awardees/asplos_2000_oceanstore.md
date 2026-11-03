# OceanStore: An Architecture for Global-Scale Persistent Storage

**Summary by:** GPT 6 Astra

**Author:** John Kubiatowicz, David Bindel, Yan Chen, Steven Czerwinski, Patrick Eaton, Dennis Geels, Ramakrishna Gummadi, Sean Rhea, Hakim Weatherspoon, Westley Weimer, Chris Wells, Ben Zhao

**Source:** ASPLOS 2000; ASPLOS Influential Paper Award 2018

**Link:** https://doi.org/10.1145/378993.379239

## Key insight

Separate durable object identity from the machines holding its bytes. Replication, encrypted storage, ordered updates, and archival fragments address different failure modes and can be combined without trusting one storage server with the whole object.

## Basic idea

OceanStore names location-independent objects [1] and permits their replicas to move and be cached across an untrusted infrastructure. Clients submit conditional updates [2], whose definitive order is chosen by a small primary replica tier rather than one trusted master. Secondary replicas disseminate and cache data with application-selected consistency requirements [3]. Immutable versions can be erasure-coded for archival durability [4], separate from the active replicas used for access and updates.

## Illustrative example

**Name and read.** A shared notebook has a stable object identifier even when its replicas change hosts. A client obtains a version through a nearby replica, with the freshness required by its session. Servers store encrypted contents rather than receiving unrestricted access to the notebook's plaintext.

**Submit a conditional change.** A client that read version 7 prepares an update: if the current version is 7, replace a specified encrypted block; otherwise abort. Another client submits a competing version-7 update. This is an instance of the paper's ordered predicate/action update format, not an arbitrary server-side program over plaintext.

**Serialize and disseminate.** The primary tier agrees on an order. If the first update changes the version, the second one's version predicate fails when evaluated afterward. Secondary replicas receive the resulting order and state through dissemination. A client accepting a tentative or stale secondary view has a different consistency contract from one requiring the definitive committed result.

**Archive a version.** Encode an immutable notebook version into fragments and distribute them across servers. A toy erasure code might reconstruct the version from any three of five valid fragments. Two missing fragments then need not lose the version, but fewer than three surviving valid fragments are insufficient. This numerical code illustrates the threshold property, not OceanStore's deployment parameters.

## Concepts and terms

**[1] Location-independent object.** A stable name identifies data independently of its current servers. Object-location mechanisms find usable replicas; encryption restricts who can read contents. Naming, confidentiality, and locating a fresh replica are distinct responsibilities.

**[2] Conditional update and primary tier.** An update lists predicates with actions; the actions for the first true predicate execute atomically, or the update aborts if none holds. Primary replicas use Byzantine agreement to choose the definitive order under that protocol's failure assumptions. Servers can perform selected operations on encrypted blocks and exposed metadata, not arbitrary encrypted computation.

**[3] Secondary replicas and consistency.** Additional replicas can hold incomplete or lagging object state and spread updates through epidemic and tree-based mechanisms. Sessions select consistency guarantees appropriate to the application. A network partition does not make strong consistency and unrestricted update availability simultaneously free.

**[4] Versioned archive and scope.** Erasure coding stores redundant fragments from which sufficiently many valid pieces reconstruct an immutable version. Durability depends on fragment availability, repair, and the fault model. The paper presents an architecture and prototype components; its design arguments are not measurements of a fully deployed global storage utility or a guarantee against every correlated failure.
