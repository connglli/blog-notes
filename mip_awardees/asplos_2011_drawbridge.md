# Rethinking the Library OS from the Top Down

**Summary by:** GPT 6 Astra

**Author:** Donald E. Porter, Silas Boyd-Wickizer, Jon Howell, Reuben Olinsky, Galen C. Hunt

**Source:** ASPLOS 2011; ASPLOS Influential Paper Award 2022

**Link:** https://doi.org/10.1145/1961296.1950399

## Key insight

Preserve the operating-system interface that an application expects inside its own library OS, while moving host interaction behind a much smaller interface. Application compatibility and resource protection need not be implemented by the same large kernel boundary.

## Basic idea

Drawbridge refactors Windows into a library operating system [1] capable of supporting existing application binaries. A narrow application binary interface, or ABI [2], supplies memory, execution, synchronization, and stream operations. A platform adaptation layer and security monitor [3] implement that ABI over host resources and enforce the application's permitted access. Keeping the rich OS personality inside the application boundary supports packaging and portability without reproducing an entire hardware-virtualized guest machine.

## Illustrative example

**Package an application.** A small existing Windows editor expects familiar library calls for creating windows, allocating memory, and opening files. Package it with the required Windows library-OS components. It continues calling those interfaces rather than being rewritten for a new minimal API.

**Open a document.** The application requests an ordinary file operation. The library OS implements its expected semantics and translates the host-facing portion into stream operations on a URI. The security monitor decides which host resources the application may access and returns a virtualized handle. The application does not gain unrestricted access to the host merely because its private library OS implements a broad API.

**Keep state private.** Application-specific OS bookkeeping belongs inside that application's library OS. The host still manages actual memory, threads, devices, and external resources through the restricted boundary. The design therefore avoids copying all host functionality into the package while preserving the application-visible personality it needs.

**Change hosts.** Another host can supply a different implementation of the same lower ABI. If it honors the required semantics, the packaged application and its library OS need not adopt that host's full operating-system API. This is compatibility through a stable abstraction, not a claim that every Windows program or every host feature is supported.

## Concepts and terms

**[1] Library OS and personality.** OS functionality linked or hosted with an application implements the application-visible API, including behavior that ordinary applications expect from system libraries and parts of the kernel. Drawbridge derives this from an existing Windows system rather than requiring applications to be written against a clean-slate library interface.

**[2] Narrow ABI.** The binary contract between the library OS and the outside system. Drawbridge exposes abstractions such as virtual memory, threads, synchronization objects, and byte streams rather than the entire Windows system-call surface. Stream operations cover several resource kinds through URI schemes. The paper deliberately balances interface size against implementation complexity.

**[3] Adaptation and security monitor.** Host-specific components implement the ABI while preserving isolation and virtualizing resource identities. The library OS is not itself the host's trusted policy enforcement boundary. Compatibility depends on consistent ABI semantics, and the prototype's demonstrated applications do not establish universal application coverage. This design is distinct from running a whole unchanged guest kernel under a virtual hardware interface.
