# Onix: A Distributed Control Platform for Large-scale Production Networks

**Summary by:** GPT 6 Astra

**Author:** Teemu Koponen, Martin Casado, Natasha Gude, Jeremy Stribling, Leon Poutievski, Min Zhu, Rajiv Ramanathan, Yuichiro Iwata, Hiroaki Inoue, Takayuki Hama, and Scott Shenker

**Source:** OSDI 2010; SIGOPS Hall of Fame Award 2021

**Link:** https://www.usenix.org/conference/osdi10/legacy-presentation/onix-distributed-control-platform-large-scale-production

## Key insight

Network-control applications can operate on a shared network-state abstraction instead of each implementing discovery, replication, and device communication. The application must still choose consistency policies appropriate to each kind of state.

## Basic idea

Onix separates control logic [1] from packet forwarding and gives that logic a Network Information Base [2] containing connected network objects. Several controller instances distribute this state using either a durable transactional database [3] or a faster, eventually consistent distributed hash table [4]. Applications read objects, update desired state, and subscribe to changes; protocol adapters synchronize relevant state with network devices. Onix supplies mechanisms for distribution but leaves application-specific conflict resolution and many failure policies to the control logic.

## Illustrative example

**Setup.** Two controllers manage switches `birch` and `cedar`. Each switch has two links to a destination. The application needs both an administrative rule, "traffic for project P may use only approved ports," and frequently changing link-utilization readings.

**Represent state.** Give switches, ports, and links stable identifiers in the NIB. Link objects reference their endpoint ports. The application registers for utilization changes and reads this graph to compute a permitted route. A NIB object is a controller-side representation; changing it is not itself proof that hardware has already accepted a forwarding rule.

**Choose distribution.** Store the administrative policy in the replicated transactional database. Group related policy edits into one database transaction. Its import/export machinery copies committed changes between the database and controller NIBs. Put utilization estimates in the in-memory DHT, where higher update rates justify tolerating delayed propagation and weaker durability.

**React and reconcile.** Suppose a DHT notification reports that one approved link is busy. The application checks the policy, chooses the other approved link, and updates the corresponding forwarding state in its NIB. A device adapter transmits that change to the switch. If two controllers publish conflicting utilization values, application logic must reconcile them or avoid concurrent writers through coordination. DHT notifications can be delayed or spuriously triggered, so a callback must examine the actual state and reinstall the soft-state trigger when necessary.

**Failure contract.** A disconnected controller can have stale observations. The platform's global data model therefore does not imply one instantly current, transactionally consistent snapshot of both stores and every switch. The application decides which actions are safe with stale observations and which require coordination or must wait.

## Concepts and terms

**[1] Control logic.** Code that decides network behavior, such as routes and access policy. Forwarding elements apply installed rules to packets; they do not have to run that complete decision procedure for every packet.

**[2] Network Information Base.** A typed graph of network entities with identifiers, attributes, and relationships. Applications interact with this graph through reads, writes, and notifications.

**[3] Durable transactional database.** Replicated storage that preserves committed updates and groups changes into atomic transactions. Onix uses it for state whose stronger consistency requirements justify its lower update throughput.

**[4] Eventually consistent distributed hash table.** A partitioned and replicated key-value store whose replicas can temporarily differ. Onix's version is memory-only and may return conflicting values; convergence requires the application to handle those conflicts appropriately.
