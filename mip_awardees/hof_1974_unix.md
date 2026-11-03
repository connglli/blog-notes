# The UNIX Time-Sharing System

**Summary by:** GPT 6 Astra

**Author:** Dennis M. Ritchie and Ken Thompson

**Source:** SOSP 1973; Communications of the ACM 17(7), 1974; SIGOPS Hall of Fame Award 2005

**Link:** https://doi.org/10.1145/361011.361061

## Key insight

A small set of compatible mechanisms can support many useful combinations. Uniform file descriptors, process creation, program replacement, and pipes let ordinary programs cooperate without embedding a special composition framework in each one.

## Basic idea

UNIX supplies a hierarchical file system [1] and a common read/write interface through file descriptors [2]. Fork [3] creates a new process with inherited open files, while program execution [4] replaces that process's program without discarding its open-file connections. Pipes [5] connect the output of one process to the input of another. The shell [6] combines these mechanisms outside the kernel, so programs using standard input and output need not know whether they are attached to a terminal, file, or another program.

## Illustrative example

**Compose tools.** Suppose two simple programs exist: `words` reads bytes and emits one word per line, while `sort` orders input lines. A user asks the shell to run a pipeline taking input from file `notes` and writing the sorted words into file `index`. The example describes the mechanics rather than assuming a particular modern shell syntax.

**Arrange descriptors.** The shell opens `notes`, creates `index`, and creates a pipe. It creates child processes and arranges the first child's standard input descriptor 0 to refer to `notes` and standard output descriptor 1 to the pipe. The second child's descriptor 0 refers to the pipe, and its descriptor 1 to `index`.

**Install programs.** Each child uses the program-execution operation to replace its inherited program image with the desired tool. Its open files remain connected as arranged. `words` uses ordinary reads and writes on descriptors 0 and 1; it does not implement file lookup or pipe creation for this particular command.

**Run concurrently.** The programs execute independently. Pipe operations coordinate producer and consumer: a read waits when appropriate for data to arrive, and the system manages the intermediate buffer. The shell closes its unnecessary pipe references and waits for the children as required. Retaining extra references carelessly can interfere with completion behavior in a pipe implementation, so descriptor lifetime is part of correct composition.

**Preserve separation.** The shell performs command interpretation and redirection, while the kernel provides processes and I/O primitives. A different user program can use those same primitives to implement another command interface. A file descriptor is a reference to an open object, not the object's pathname; inheritance therefore preserves a connection without making children reopen every name.

This summarizes the mechanisms described in the 1974 paper. Their historical call signatures and shell notation differ from modern POSIX interfaces, so the example deliberately avoids presenting modern C calls as verbatim historical code.

## Concepts and terms

**[1] Hierarchical file system.** Directories organize names leading to files and other directory entries. Protection controls access independently of how programs combine I/O streams.

**[2] File descriptor.** A process-local handle used for operations on an open file, device, or pipe. Standard input and output conventionally use descriptors 0 and 1.

**[3] Fork.** Creation of another process with an independent program-data image and inherited references to open files, allowing parent and child to proceed separately.

**[4] Program execution.** Replacing a process's current code and data with a named executable while retaining the described open-file and process relationships.

**[5] Pipe.** An interprocess channel accessed through the file-I/O interface, allowing a producer's output to become a consumer's input.

**[6] Shell.** A user-level command interpreter that creates processes and establishes their I/O connections rather than requiring this orchestration inside each application.
