# VAXclusters: A Closely-Coupled Distributed System

**Summary by:** GPT 6 Astra

**Author:** Nancy P. Kronenberg, Henry M. Levy, and William D. Strecker

**Source:** SOSP 1985; full paper in ACM Transactions on Computer Systems 4(2), 1986; SIGOPS Hall of Fame Award 2009

**Link:** https://doi.org/10.1145/214419.214421

## Key insight

Separate computers can present shared files and resources coherently if membership, communication, and locking are designed together. Shared disk access needs cluster-wide coordination and a rule preventing disconnected groups from acting as independent owners of the same storage.

## Basic idea

VAXclusters combine independent VAX/VMS nodes with shared storage and an interconnect [1] designed for efficient communication. A distributed lock manager [2] coordinates named resources, while a distributed directory [3] locates the node mastering each resource's lock state. A quorum membership rule [4] prevents incompatible partitions from continuing unrestricted access to shared resources. Recovery reconstructs coordination state after node loss so surviving nodes can continue when the required membership and storage remain available.

## Illustrative example

**Name a shared resource.** Nodes A, B, and C can access the same disk volume. An application treats record `orders/17` as a lockable resource beneath its file and volume. It requests an appropriate exclusive lock before modifying the record, using the same interface regardless of which node runs the process.

**Find the master.** Hashing or otherwise mapping the resource name identifies its directory node. That node supplies the resource master, which maintains granted locks and queued requests. Suppose A masters this resource and grants B the exclusive lock. A conflicting request from C waits until B releases or converts its lock under the compatibility rules.

**Lose a node.** If A fails, surviving nodes cannot simply invent new independent lock histories. Cluster recovery reestablishes the lock manager's state using information retained by nodes holding locks and the membership protocol. If B failed while holding a lock, application or file-system recovery may also be needed before releasing protection exposes a partially completed update. Lock release alone does not undo disk writes.

**Split the network.** Give each of the three nodes one vote and require two votes to operate. A partition containing A and B can meet that requirement, while isolated C cannot. C suspends the relevant process activity rather than continuing to grant incompatible access to the same shared disk. The configuration must preserve the quorum-intersection property; choosing thresholds independently during a split would defeat it.

The architecture trades availability of a minority partition for shared-resource integrity. Its communication hardware reduces overhead but does not replace locking. Conversely, a distributed lock manager without coordinated membership would not prevent two disconnected masters from each believing they control one resource.

## Concepts and terms

**[1] Interconnect.** The communication hardware and protocols joining nodes and storage controllers. The paper's design offloads message-transfer functions to communication ports rather than requiring all work in host software.

**[2] Distributed lock manager.** A service granting compatible access modes to named resources and queuing incompatible requests. Locks are cooperative synchronization; applications and storage services must use them consistently.

**[3] Resource directory and master.** The directory maps a resource name to the node responsible for its lock state. The master tracks granted requests and waiters for the resource tree it controls.

**[4] Quorum membership rule.** A configured voting threshold determining whether a cluster may continue. Properly chosen thresholds prevent disjoint partitions from both operating as the valid cluster over shared resources.
