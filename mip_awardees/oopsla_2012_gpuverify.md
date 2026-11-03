# GPUVerify: A Verifier for GPU Kernels

**Summary by:** GPT 6 Astra

**Author:** Adam Betts, Nathan Chong, Alastair Donaldson, Shaz Qadeer, Paul Thomson

**Source:** OOPSLA 2012; SIGPLAN Most Influential OOPSLA Paper Award, 2022

**Link:** https://doi.org/10.1145/2384616.2384625

**Code:** [GPUVerify](https://github.com/mc-imperial/gpuverify)

## Key insight

Checking two arbitrary threads can expose a conflicting access or mismatched barrier, provided the effects of the omitted threads are conservatively represented.

## Basic idea

GPUVerify transforms a GPU kernel [1] into a sequential verification problem for two distinct symbolic threads. Predicated execution [2] records which thread is active, while access logging checks intra-group data races [3] and barriers check divergence [4]. Shared-memory abstraction [5] accounts for threads not explicitly modeled. The OOPSLA 2012 paper targets intra-group races and barrier divergence, not complete functional correctness or general inter-group race freedom.

## Illustrative example

**Kernel.** A group has four threads numbered zero through three. Each writes its identifier into `scratch[id]`, all execute the same barrier, then each reads `scratch[(id+1) % 4]` into a private variable. Assume `scratch` has four elements and the barrier fences this shared memory.

**Symbolic pair.** Choose arbitrary distinct identifiers `u` and `v` in that range. The first writes access `scratch[u]` and `scratch[v]`, so no write/write conflict is possible. At the barrier both threads are enabled; access records for the completed interval can be reset. The later accesses are reads only, so they do not conflict with each other. The barrier separates them from the earlier writes.

**Missing barrier.** Delete the barrier. For `u = 0` and `v = 1`, u's read of `scratch[1]` can conflict with v's write. Symbolic identifiers let the verifier find this pair without enumerating every schedule of four concrete threads.

**Divergence and abstraction.** Instead place the barrier inside `if (id < 2)`. The pair `u = 0`, `v = 2` has different enabled flags there, exposing divergence. In the safe version, reads may be abstracted to arbitrary values because only their addresses matter to this proof. This intentionally loses the ability to conclude the numerical result of each read. When control depends on shared values, the paper's equality abstraction can retain agreement between threads after barriers without reconstructing every omitted thread's writes.

## Concepts and terms

**[1] GPU kernel.** A program run by many threads organized into groups sharing synchronization facilities.

**[2] Predicated execution.** Execute a combined control structure while guarding each thread's effects by its active flag.

**[3] Intra-group data race.** Unordered conflicting accesses by distinct threads of one group, at least one a write.

**[4] Barrier divergence.** Threads in a group disagree about participating in the same dynamic barrier.

**[5] Shared-memory abstraction.** Replace concrete shared values by a conservative approximation, preserving possible errors while potentially introducing false alarms.
