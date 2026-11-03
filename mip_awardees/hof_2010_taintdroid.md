# TaintDroid: An Information-Flow Tracking System for Realtime Privacy Monitoring on Smartphones

**Summary by:** GPT 6 Astra

**Author:** William Enck, Peter Gilbert, Byung-Gon Chun, Landon P. Cox, Jaeyeon Jung, Patrick McDaniel, and Anmol N. Sheth

**Source:** OSDI 2010; SIGOPS Hall of Fame Award 2020

**Link:** https://www.usenix.org/conference/osdi10/taintdroid-information-flow-tracking-system-realtime-privacy-monitoring

**Code:** [TaintDroid source repositories](https://github.com/TaintDroid)

## Key insight

Tracking sensitive data at different granularities across the runtime, interprocess messages, and files makes phone-wide monitoring practical. A permission to obtain data need not imply permission to send every derived value to a remote server.

## Basic idea

TaintDroid labels sensitive sources and propagates taint tags [1] through an Android system until data reaches a monitored sink [2]. It tracks variables inside the Dalvik interpreter [3], summarizes supported native methods [4], and uses coarser tags for interprocess messages and files. Combining these mechanisms follows explicit data flows across application boundaries without instrumenting every machine instruction. The monitor detects potentially sensitive transmissions, but neither establishes malicious intent nor captures every implicit flow [5].

## Illustrative example

**Label and compute.** A weather application receives latitude from the location service, tagged `LOCATION`. In its interpreted code, it divides that value into a coarse region number and combines the result with an ordinary request identifier. The tag on each arithmetic result includes the tags of its inputs, so coarsening the location does not silently erase its origin.

**Cross boundaries.** The application formats the result using a supported native routine. A method-specific propagation rule transfers the relevant input taint to the returned data without tracing the native machine instructions. It sends a Binder message containing the region and request identifier to an upload service. The parcel carries the union of the message's tags; values unmarshaled from it inherit that parcel tag.

If the upload service saves the message to a file, file-level tracking preserves the taint across the write and later read. This deliberately sacrifices precision: unrelated data read from the same tainted file can also become tainted. Arrays similarly have a single tag rather than a separate tag for every element.

**Inspect the sink.** When the service sends the saved bytes over a monitored network interface, TaintDroid sees `LOCATION` on the outgoing data and records the transmission. An application may legitimately send a region to obtain a forecast. The tag identifies provenance for a policy decision or investigation, not whether the user consented.

**Boundary of the result.** If the application instead tests a secret and chooses between two independently created constants, the secret can influence which constant is sent without an explicit data dependency. TaintDroid does not track this implicit flow. Its design also restricts untrusted applications' native-library loading; arbitrary uninstrumented native code would otherwise bypass the interpreter's propagation rules.

## Concepts and terms

**[1] Taint tag.** Metadata indicating sensitive origins that may have influenced a value. TaintDroid uses a 32-bit tag and combines origins using bitwise union during propagation.

**[2] Source and sink.** A source introduces data requiring tracking, such as location. A sink is an operation where the system examines tags, such as a network send.

**[3] Dalvik interpreter.** Android's runtime for executing application bytecode. Extending its value-handling operations lets the monitor propagate tags alongside program values.

**[4] Native-method summary.** A rule describing how tags move between arguments and results of a trusted machine-code method. Correctness depends on the rule matching that method's behavior.

**[5] Implicit flow.** Information conveyed through control decisions rather than direct copying or arithmetic on sensitive values.
