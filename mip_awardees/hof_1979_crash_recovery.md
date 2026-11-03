# Crash Recovery in a Distributed Data Storage System

**Summary by:** GPT 6 Astra

**Author:** Butler W. Lampson and Howard E. Sturgis

**Source:** Unpublished manuscript, Xerox PARC, 1979; SIGOPS Hall of Fame Award 2010

**Link:** https://bwlampson.site/21-CrashRecovery/WebPage.html

## Key insight

Reliable transactions can be built as a hierarchy of small crash-aware abstractions. A durable decision separates tentative intentions from changes that recovery must complete, even if several servers crash at inconvenient points.

## Basic idea

The paper derives stable storage [1] from a stated disk-failure model, then builds restartable actions [2] and protected persistent structures above it. A transaction records its intended updates [3] and locks [4] before an atomic phase change [5] commits it. Only committed intentions are applied to the stored data; after interruption, recovery can repeat the necessary actions safely. Correctness is conditional on the assumptions at each layer, including storage faults, communication behavior, and recovery execution.

## Illustrative example

**Construct a stable page.** Represent one logical page by two ordered physical copies with detectable read/write status. A careful write writes and reads back until it confirms the requested value, subject to the model's error bounds. A stable write updates the first copy successfully before starting the second. If a crash leaves one bad copy, cleanup repairs it from the good one; if both are good but differ, cleanup resolves the interrupted write according to the ordered-copy rule.

This is not a claim that two disks survive any correlated destruction. The construction relies on the modeled separation and detectability of failures and explicitly distinguishes unexpected disasters from tolerated events.

**Record a transaction.** A transfer changes balance X from 12 to 9 and balance Y from 8 to 11, stored at different servers. Begin creates a transaction identifier. The writes record intentions for the new values while acquiring the necessary locks; they do not expose a half-completed transfer. The client waits for every requested write to return before requesting End.

**Decide and complete.** End atomically changes the persistent transaction phase from running to committed. That is the decision boundary. The system then applies the recorded new values. If a server crashes after X is written but before Y, recovery observes committed status and finishes the intentions, repeating already completed assignments if necessary.

If the transaction aborts instead, its intentions are discarded without publishing the transfer. Locks prevent other transactions from observing or interfering with the intermediate state. Cleanup removes intentions and corresponding locks only under the protocol's ordering constraints.

The decision is durable even when its reply is lost; a client must use the transaction protocol rather than assume silence means abort. Availability can wait for recovery or communication. The construction's guarantee is atomic behavior under its model, not uninterrupted progress despite every possible failure.

## Concepts and terms

**[1] Stable storage.** An abstraction presenting reliable reads and atomic page writes despite the explicitly modeled physical-storage errors. Its implementation and limits are part of the correctness argument.

**[2] Restartable action.** An operation whose recovery can safely resume or repeat it after interruption, with persistent state distinguishing the necessary remaining work.

**[3] Intention.** A persistent description of a proposed data update, associated with its transaction, retained until commitment and cleanup determine its disposition.

**[4] Lock.** A restriction on concurrent access that prevents other transactions from observing incompatible intermediate states. Persistent transaction state and lock cleanup must remain coordinated across crashes.

**[5] Atomic phase change.** A durable transition that chooses committed or aborted status exactly once. It decides whether recovery must install the transaction's updates or discard them.
