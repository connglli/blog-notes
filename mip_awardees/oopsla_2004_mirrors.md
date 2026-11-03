# Mirrors: Design Principles for Meta-level Facilities of Object-Oriented Programming Languages

**Summary by:** GPT 6 Astra

**Author:** Gilad Bracha, David Ungar

**Source:** OOPSLA 2004; SIGPLAN Most Influential OOPSLA Paper Award, 2014

**Link:** https://doi.org/10.1145/1028976.1029004

## Key insight

Objects that implement an application need not also implement every operation for inspecting and manipulating that application's structure.

## Basic idea

Mirror-based reflection [1] places metaprogramming operations on separate mirror objects. Three principles guide the API: encapsulation [2], stratification [3], and correspondence [4] with the language's entities. This separation allows different implementations, including remote inspection, without forcing the application's base objects to expose implementation-specific reflection methods. Mirrors organize reflective authority and deployment; their existence alone is not a complete security policy.

## Illustrative example

**Application.** An `Invoice` object offers domain operations such as adding a line item and computing a total. A debugging tool wants to list its fields and inspect their current values. Instead of adding debugging methods to every application object, give the tool an object mirror obtained through a reflection service.

**Interface.** The object mirror can supply a class mirror; the class mirror enumerates field and method mirrors. A field mirror reads the relevant slot from the mirrored invoice under the API's access rules. The debugger uses these abstract interfaces rather than depending on the virtual machine's object-header layout.

**Remote implementation.** A different reflection service supplies mirrors backed by communication with another process. The same debugger can ask for field information through the interface, although latency, object identity, failures, and permitted operations require explicit semantics. It should not mistakenly operate on the local proxy's class when it intends to inspect the remote invoice's class.

**Separation.** Deploying the invoice application need not automatically deploy the entire debugger and reflective API. Conversely, a source-oriented browser may need mirrors for declarations that have no current runtime instance. Correspondence asks the reflective model to represent such distinctions faithfully, rather than forcing every concept into a misleading runtime-object category. The implementation may vary while the tool's view of fields, methods, and declarations remains coherent.

## Concepts and terms

**[1] Reflection.** Programs inspecting or manipulating program structure or execution; a mirror is a separate object exposing such operations for another entity.

**[2] Encapsulation.** Hide reflective implementation details behind interfaces, permitting alternative implementations.

**[3] Stratification.** Separate application-level operations from reflective operations so either layer can be deployed and reasoned about independently.

**[4] Correspondence.** Reflective entities and relationships should match those of the language being represented, including distinctions between source and execution levels.
