# Pin: Building Customized Program Analysis Tools with Dynamic Instrumentation

**Summary by:** GPT 6 Astra

**Author:** Chi-Keung Luk, Robert Cohn, Robert Muth, Harish Patil, Artur Klauser, Geoff Lowney, Steven Wallace, Vijay Janapa Reddi, Kim Hazelwood

**Source:** PLDI 2005; SIGPLAN Most Influential PLDI Paper Award, 2015

**Link:** https://doi.org/10.1145/1065010.1065034

**Documentation:** [Intel Pin](https://www.intel.com/content/www/us/en/developer/articles/tool/pin-a-dynamic-binary-instrumentation-tool.html)

## Key insight

Separate deciding where to insert observations from executing those observations, and let dynamic compilation remove much of the instrumentation overhead.

## Basic idea

A Pintool supplies instrumentation routines [1] that inspect code as Pin translates it and analysis routines [2] that run with the application. Pin dynamically compiles native instructions into a code cache [3], inserting the requested observations and preserving application state. Its API supplies instruction properties and runtime values without requiring each tool to implement instruction decoding and register preservation. Optimization can inline small analysis routines and eliminate unnecessary state saving.

## Illustrative example

**Policy.** Measure how many bytes a single-threaded program attempts to write to memory. At instrumentation time, inspect each instruction and select memory-writing instructions. Insert an analysis call immediately before each such instruction, passing its runtime destination address and write size.

**Runtime.** A four-byte store executed in a loop three times calls the analysis routine three times, adding twelve bytes to the counter. The instrumentation callback that chose this placement need not run three times: the translated instruction and inserted call can be reused from the cache. A different instruction writing eight bytes increases the total to twenty.

**Interpretation.** Because the observation is before the store, a store that faults may still be counted. The metric is therefore attempted bytes written, not successfully committed bytes. Also, a machine instruction can require handling beyond this simple single-destination case; a complete tool must follow the API's semantics for those instructions rather than extrapolating from this example.

**Transparency.** Incrementing the tool's counter may clobber machine condition flags. Pin must preserve any flags the application needs afterward. If a flag is dead at this point, saving it is unnecessary. Inlining a tiny counter update can remove calls while preserving the same observation. Multithreaded counting would additionally require thread-local counters or correct synchronization in the tool.

## Concepts and terms

**[1] Instrumentation routine.** A translation-time callback that chooses where and how to add analysis code.

**[2] Analysis routine.** A runtime operation that records or checks an event, using constants or application-state arguments supplied by Pin.

**[3] Code cache.** Storage for generated executable translations, allowing repeated execution without decoding and reinstrumenting every occurrence.
