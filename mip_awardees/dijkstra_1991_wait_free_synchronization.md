# Wait-free synchronization

**Summary by:** GPT 6 Astra

**Author:** Maurice Herlihy

**Source:** ACM Transactions on Programming Languages and Systems 13(1), 1991; Edsger W. Dijkstra Prize in Distributed Computing 2003.

**Link:** https://doi.org/10.1145/114005.102808

## Key insight

The ability to solve consensus measures the synchronization power of a shared object. It supplies both impossibility results for implementing stronger objects from weaker ones and a route to general wait-free constructions.

## Basic idea

A wait-free operation [1] completes after finitely many of its caller's own steps regardless of other processes' speeds or failures. An object's consensus number [2] is the maximum number of processes for which copies of that object, together with read/write registers, can solve consensus. The hierarchy separates primitives such as registers from stronger synchronization objects. A universal construction [3] uses sufficiently powerful consensus objects and helping [4] to implement a sequential object's operations in a shared, agreed order.

## Illustrative example

**One consensus instance.** Three processes propose values 4, 7, and 9. They share an atomic compare-and-swap location `winner` initially containing an empty marker distinct from every proposal.

Each process attempts to replace empty with its proposal. Exactly one successful replacement can occur: suppose the proposal 7 wins. Every process then reads and decides the nonempty value in `winner`. Losing processes do not retry until they win; they adopt the winner.

If the winning process stops immediately after its successful replacement, the other processes can still read 7. The result is a proposed value, all decisions agree, and each participating process uses a bounded number of its own operations. The same construction works for any fixed number of processes.

**Why ordinary registers differ.** Replacing compare-and-swap by a separate read followed by a write is not atomic. Two processes can both observe empty, then write different proposals and decide inconsistently. This failed replacement is an illustration, not the hierarchy's full impossibility proof.

**From one choice to an object.** To implement a counter, use consensus to agree on which announced increment is next in a shared operation history. Replay the chosen operation on the preceding sequential state, recording its result. Subsequent consensus instances extend the history.

A process must also help older pending requests enter the history. Without a helping discipline, a process might lose every contest and starve even while the system makes progress. A simple retrying compare-and-swap loop is therefore not automatically a wait-free implementation.

## Concepts and terms

**[1] Wait-free operation.** An operation whose active caller cannot be prevented from completing by arbitrary delay or stopping of other processes. The guarantee counts the caller's steps, not elapsed wall-clock time.

**[2] Consensus number.** A synchronization-power classification defined by wait-free consensus solvability. Registers have consensus number 1, while compare-and-swap has unbounded consensus number.

**[3] Universal construction.** A method implementing an arbitrary sequentially specified object by agreeing on an operation sequence and computing the corresponding sequential states and responses.

**[4] Helping.** Executing or completing the shared representation of another process's announced operation so its progress does not require that process to run. A wait-free construction needs a discipline preventing indefinite postponement of any request.

