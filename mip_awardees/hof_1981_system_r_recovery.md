# The Recovery Manager of the System R Database Manager

**Summary by:** GPT 6 Astra

**Author:** Jim Gray, Paul McJones, Mike Blasgen, Bruce Lindsay, Raymond Lorie, Tom Price, Franco Putzolu, and Irving Traiger

**Source:** ACM Computing Surveys 13(2), 1981; SIGOPS Hall of Fame Award 2010

**Link:** https://doi.org/10.1145/356842.356847

## Key insight

A shared database needs recovery at transaction granularity, not just restoration of whole files. Logs identify each transaction's changes, while a consistent shadow checkpoint provides a recoverable starting image.

## Basic idea

System R combines shadow versions [1] with a transaction log [2] to support commit, abort, and partial rollback to save points [3]. Recoverable operations supply DO, UNDO, and REDO behavior [4] and enough logged information to reverse or repeat their changes. Checkpoints [5] record an action-consistent database image plus transaction information without waiting for every transaction to finish. Restart uses that image and the log to preserve committed work and remove incomplete or aborted work. The paper evaluates this concrete combination rather than claiming that shadow paging alone solves concurrent transaction recovery.

## Illustrative example

**Make independent changes.** A database has account X with 20 units and account Y with 30. Transaction A subtracts 3 from X, while transaction B changes Y's address field. Their operations produce log records with transaction identities and the information needed to undo or redo the specific changes. The records share a system log but remain attributable to their transactions.

**Checkpoint amid activity.** Suppose B commits while A is still active. At a safe boundary between storage-system actions, a checkpoint records the active transactions and relevant log positions, forces the necessary log information, and saves the current logged files as the new shadow state. The checkpoint can therefore contain effects of active A. It is consistent at the action level, not necessarily the result of committed transactions alone.

**Crash and restart.** After a crash, the shadow image provides a known physical starting point. Log analysis identifies the transactions and actions whose effects need recovery. A's uncommitted debit must be removed, while B's committed change must survive. Whole-file rollback would be wrong if A and B changed different records within the same file: it would discard B's valid work together with A's.

**Use a save point.** During a retry, A establishes a save point before an optional fee calculation. If that calculation fails, A can undo changes back to the save point without discarding earlier work in the same transaction. A save point is not a commit: the remaining transaction can still abort, taking its earlier uncommitted effects with it.

**Extend recovery.** A new recoverable object type needs operations whose log records support its own correct UNDO and REDO. Logging a high-level label with insufficient information does not make arbitrary external actions reversible. The paper specifically treats message recovery as an important omission in the described system, so a database commit must not be mistaken for a complete exactly-once network-output protocol.

## Concepts and terms

**[1] Shadow version.** A stable saved file version that is not overwritten while a separate current version changes. Saving replaces the recovery image; restoring discards current changes back to it.

**[2] Transaction log.** Records identifying updates and their transactions, with sufficient old/new or operation-specific information for recovery.

**[3] Save point.** A position within a transaction to which selected later work can be rolled back without ending the entire transaction.

**[4] DO, UNDO, REDO.** Performing an update, reversing its effect, and reapplying it during recovery. Their implementations must match the logged representation and object semantics.

**[5] Action-consistent checkpoint.** A saved image taken between complete low-level storage actions, possibly while higher-level transactions remain active. Transaction log information is needed to recover a transaction-consistent state from it.
