# Multiparty asynchronous session types

**Summary by:** GPT 6 Astra

**Author:** Kohei Honda, Nobuko Yoshida, and Marco Carbone

**Source:** POPL 2008; SIGPLAN Most Influential POPL Paper Award 2018.

**Link:** https://doi.org/10.1145/1328438.1328472

## Key insight

A protocol involving several participants should be checked against one global conversation, not only unrelated pairwise interfaces. Projecting a coherent global type gives each participant a compatible local communication contract.

## Basic idea

A global session type [1] describes message transfers and choices across an entire conversation. Projection [2] derives local session types [3] that specify the sends and receives each participant must perform. The calculus models asynchronous communication with message queues [4], and checks conditions that avoid confused uses of shared session channels. Well-typed executions preserve the specified communication structure; the paper's progress result additionally restricts interleaving of sessions.

## Illustrative example

**Protocol.** Three roles collaborate on a request: Client sends an integer job number to Broker; Broker sends that number to Worker; Worker sends an integer answer to Client; the session ends. Use a distinct session channel for each of these transfers.

**Projection.** Client's local type is: send an integer to Broker, receive an integer from Worker, end. Broker's type is: receive an integer from Client, send an integer to Worker, end. Worker's type is: receive an integer from Broker, send an integer to Client, end.

Each implementation is checked against its local sequence. A Worker that sends a Boolean instead of an integer is rejected. A Broker that tries to receive a reply from Client before forwarding the job does not follow its projected type.

**Asynchronous execution.** Client can enqueue job 17 before Broker runs. Broker dequeues 17 and enqueues it for Worker. Worker dequeues the job, computes an answer such as 34, and enqueues 34 for Client. Sending and receiving are different steps; the queue contains the intermediate message and is included in the runtime typing.

The type specifies the payload sort and communication structure, not the application formula relating answer and job. Returning 35 would still satisfy this session type unless a richer specification imposed the doubling relationship.

**Progress boundary.** With all roles participating in this single session, the communication order contains no circular wait. Arbitrarily composing well-typed sessions can introduce a different cycle: one role waits in session A before acting in B, while another waits in B before acting in A. The paper's simple-process restriction excludes this obstacle in its progress theorem. Local session typing alone is not a universal deadlock-freedom theorem for unrestricted multi-session applications.

## Concepts and terms

**[1] Global session type.** A description of an entire conversation, including participants, channels, payload types, choices, and recursive continuation structure.

**[2] Projection.** Extracting one role's actions from the global description while checking that the resulting views are compatible. Not every arbitrary global description has a valid projection.

**[3] Local session type.** A stateful communication contract: executing a send, receive, or branch advances the endpoint to its continuation type.

**[4] Asynchronous queue.** Ordered storage for messages sent but not yet received on a session channel. Runtime typing accounts for queued messages as well as the remaining process actions.

