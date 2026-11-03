# Implementing Jalapeño in Java

**Summary by:** GPT 6 Astra

**Author:** Bowen Alpern, C. R. Attanasio, John J. Barton, Anthony Cocchi, Susan Flynn Hummel, Derek Lieber, Mark Mergen, Ton Ngo, Janice C. Shepherd, Stephen Smith

**Source:** OOPSLA 1999; SIGPLAN Most Influential OOPSLA Paper Award, 2009

**Link:** https://doi.org/10.1145/320384.320418

**Code:** [Jikes RVM](https://github.com/JikesRVM/JikesRVM)

## Key insight

A Java virtual machine can run its own Java implementation directly as machine code if another virtual machine constructs its initial executable state and a small trusted interface supplies operations outside Java.

## Basic idea

Jalapeño places application code and most virtual-machine services [1] in the same language, permitting ordinary calls and optimization across their boundary. A boot-image writer [2] runs on an existing JVM, constructs the required runtime objects, compiles methods, and translates the resulting object graph into Jalapeño's memory layout. A small native launcher loads that image and transfers control to its boot method. Compiler-recognized MAGIC operations [3] give trusted runtime code low-level capabilities, while special restrictions protect interactions with garbage collection [4].

## Illustrative example

**Construct.** Consider a tiny runtime whose loader and compiler both refer to one class-description object. Run their initialization methods on a host JVM and compile their required methods for the target machine. The boot image must contain the runtime classes needed to load further classes; omitting a loader dependency can make loading recurse into itself.

**Translate.** Suppose the shared class description receives target address 4096 and the loader receives address 4160. Walk the graph from the runtime's root table. For each object, allocate target space once and record a host-object-to-target-address mapping. Read its fields through reflection and write them at the target layout's offsets. Both references to the class description become 4096, preserving sharing even if the host JVM uses different addresses or object headers. Include compiled code, an initial thread and stack, and the boot record needed by the launcher.

**Start.** The native launcher loads the image, initializes the required registers, and branches to the boot method. The boot method opens operating-system resources and creates execution threads; such resources cannot simply be copied from the host JVM's initialization run.

**Cross the trusted boundary.** An allocator needs to write an object header at a raw address. Its MAGIC call is replaced by machine instructions, not executed as an ordinary Java method. If runtime code keeps an object's raw address while a copying collector moves the object, the address becomes stale. Jalapeño disables collection around such short computations and forbids operations there, including allocation and potentially blocking locking, that could require collection to make progress. Ordinary Java's safety guarantees do not justify arbitrary runtime use of MAGIC.

## Concepts and terms

**[1] Virtual-machine services.** The class loading, compilation, allocation, and execution machinery supporting Java programs.

**[2] Boot-image writer.** A program converting initialized runtime objects and code into a loadable target-memory image; reflection exposes object fields without assuming the host JVM's layout.

**[3] MAGIC operation.** A trusted compiler intrinsic for operations such as raw memory access, register manipulation, or unsafe reference conversion. Application code must not obtain these capabilities.

**[4] Garbage collection.** Automatic reclamation of unreachable objects; a copying collector also relocates live objects and updates tracked references, but not untracked raw addresses.
