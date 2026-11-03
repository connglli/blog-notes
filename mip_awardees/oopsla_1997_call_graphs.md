# Call Graph Construction in Object-Oriented Languages

**Summary by:** GPT 6 Astra

**Author:** David Grove, Greg DeFouw, Jeffrey Dean, Craig Chambers

**Source:** OOPSLA 1997; SIGPLAN Most Influential OOPSLA Paper Award, 2007

**Link:** https://doi.org/10.1145/263698.264352

## Key insight

Call targets and value-flow information depend on one another, and many competing analyses differ mainly in which invocation and object contexts they keep separate.

## Basic idea

The paper gives a parameterized framework for constructing conservative call graphs [1]. It propagates possible classes or abstract objects through variables, arguments, fields, and returns while adding targets for dynamic calls. Contours [2] distinguish selected contexts [3], and a worklist [4] revisits dependent analyses when information changes. More distinctions can improve precision but increase cost; the framework supports systematic comparisons rather than asserting one analysis is best for every program.

## Illustrative example

**Program.** A helper `relay(x)` returns `x`. One caller passes a newly created `Square`; another passes a newly created `Circle`. Each then invokes `draw` on the returned value, and the two classes provide distinct implementations.

**Merged analysis.** With one shared contour for `relay`, its parameter can contain either class. Its return set therefore contains both. Both callers receive that union, so both final call sites may have edges to `Square.draw` and `Circle.draw`. This includes the real edges, but also edges that these particular executions cannot take.

**Separated analysis.** With distinct contours for the two call sites, the first helper instance has parameter and return set `{Square}`, while the second has `{Circle}`. The final calls can each have one target. The program still has one source helper; contours are analysis records, not necessarily emitted machine-code copies.

**Fixed point.** When a new call edge is added, propagate actual arguments to its callee contour. If that changes a return set, revisit callers that consumed the old set. If objects are stored in fields, propagate through the selected field and object contours as well. Stop only when the constraints are stable, not after a single syntactic traversal. Unmodeled dynamic loading or reflection would require conservative treatment before applying whole-program conclusions.

## Concepts and terms

**[1] Conservative call graph.** A graph including every possible call target under the analysis's program model, potentially including extra edges.

**[2] Contour.** A context-indexed abstract instance of a procedure, class, or field used to hold separate analysis facts.

**[3] Context sensitivity.** Distinguishing invocations or objects using selected information such as call sites or argument classes instead of merging them all.

**[4] Worklist.** A queue of analysis units needing reconsideration because a fact they depend on has changed.
