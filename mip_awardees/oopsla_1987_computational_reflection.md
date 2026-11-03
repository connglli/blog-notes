# Concepts and Experiments in Computational Reflection

**Summary by:** GPT 6 Astra

**Author:** Pattie Maes

**Source:** OOPSLA 1987; SIGPLAN Most Influential OOPSLA Paper selection for 1986-1996 (retrospective award)

**Link:** https://doi.org/10.1145/38765.38821

## Key insight

A program can reason about and modify its own computation when its self-representation is connected to the mechanism actually executing it.

## Basic idea

Computational reflection [1] combines a self-representation with a causal connection [2] between that representation and execution. The paper's 3-KRS experiment uses meta-objects [3] describing object interpretation, including message handling and evaluation. Specializing a meta-object can change how an ordinary object is interpreted without rewriting its domain behavior. The reflective mechanism is itself programmable, but a descriptive data structure alone is insufficient unless the interpreter honors it.

## Illustrative example

**Ordinary computation.** A document object answers a `render` message by producing a string. We want to trace message evaluation for this document temporarily, without adding logging to the document's rendering method or changing other documents.

**Self-representation.** Associate a meta-object describing the message-evaluation behavior with the relevant program object. The interpreter consults that meta-object when evaluating the message. A standard evaluation method performs the ordinary computation.

**Specialization.** Create a tracing meta-object that delegates to the original one but overrides evaluation: record the message before delegation, invoke the original evaluation, then record the returned value. Attach it in place of the original meta-object. Sending `render` produces the same intended rendering result plus the tracing observations, assuming the added logging itself completes without interfering with the computation.

**Connection.** Removing the tracing meta-object restores ordinary evaluation. If the attachment were only a field in a debugger's private data structure and the interpreter never consulted it, no tracing would occur. That missing operational link distinguishes passive description from reflection. The meta-level also needs disciplined delegation: calling its own override repeatedly instead of the underlying evaluator could recurse indefinitely.

## Concepts and terms

**[1] Computational reflection.** Computation about a system's own structure or activity, with effects on that system's computation.

**[2] Causal connection.** The representation and represented system stay linked, so relevant changes to one affect the other.

**[3] Meta-object.** An object representing implementation or interpretation aspects of another object; the interpreter uses its specified behavior rather than treating it as inert descriptive data.
