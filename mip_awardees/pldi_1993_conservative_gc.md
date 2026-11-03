# Space Efficient Conservative Garbage Collection

**Summary by:** GPT 6 Astra

**Author:** Hans-Juergen Boehm

**Source:** PLDI 1993; SIGPLAN Most Influential PLDI Paper Award, 2003

**Link:** https://doi.org/10.1145/155090.155109

**Code:** [Boehm-Demers-Weiser collector](https://github.com/ivmai/bdwgc)

## Key insight

An integer that looks like a pointer need not retain a large future allocation: remember suspicious addresses and avoid placing vulnerable objects there.

## Basic idea

A conservative collector [1] may retain garbage because an untyped word resembles a pointer. Blacklisting [2] records pointer-like values that currently point to unallocated storage, then constrains later allocation around them. This reduces false retention [3], especially when an accidental reference would retain an object that reaches many others. The method cannot infer all true pointer identities or guarantee that every unreachable object is reclaimed.

## Illustrative example

**Near miss.** Suppose a long-lived integer has bits equal to address `0x4200`. That address lies in a currently unused heap page. During a collection, the scanner encounters this word but finds no allocated object there. Instead of forgetting the event, it marks the corresponding allocation region as suspicious.

**Without avoidance.** A later allocation places a list node at `0x4200`. The node points to a long list. Once the application loses its real reference to the list, the integer can still look like a root to the head node. Tracing from that apparent root retains the entire reachable chain.

**With avoidance.** Place pointer-containing objects somewhere else. If permitted by the allocation policy, use the suspicious region for small pointer-free objects. An accidental reference can then retain only a limited amount of data rather than a graph of linked objects. If interior pointers are recognized, avoiding only an object's starting address is insufficient: a suspicious address inside a large object can retain it too.

**Boundary.** A genuinely live pointer must still be respected, even when its target address looks inconvenient. Blacklisting uses known near misses to influence future placement; it does not authorize ignoring arbitrary pointer-looking roots. Separately, stale real pointers in stack slots and poorly structured long-lived objects can retain memory even without integer misidentification, so allocation policy cannot solve every retention problem.

## Concepts and terms

**[1] Conservative collector.** A collector lacking exact pointer-location information and therefore treating some plausible pointer bit patterns as references.

**[2] Blacklisting.** Recording suspicious target regions and restricting future object placement there.

**[3] False retention.** Keeping otherwise unreachable storage because conservative tracing finds an apparent reference. Its transitive cost can exceed the size of the directly retained object.
